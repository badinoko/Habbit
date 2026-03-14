from urllib.parse import urlencode, urlsplit

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from src.config import settings
from src.csrf import csrf_error_message, read_request_payload, validate_csrf
from src.dependencies import get_auth_service, get_current_user, require_auth
from src.exceptions import (
    EmailAlreadyExistsError,
    OAuthAuthorizationCodeMissingError,
    OAuthConfigurationError,
    OAuthEmailNotVerifiedError,
    OAuthIdentityAlreadyLinkedToAnotherUserError,
    OAuthProviderRejectedError,
    OAuthProviderUnavailableError,
    OAuthStateInvalidError,
    UserIsInactiveError,
)
from src.schemas import AuthLogin, AuthRegister, AuthUser
from src.services.auth import AuthService
from src.utils import ensure_csrf_token, get_user_display_name, templates

router = APIRouter(prefix="/auth", tags=["auth"])
_DEFAULT_REDIRECT_PATH = "/"
_GOOGLE_OAUTH_UI_SESSION_KEY = "google_oauth"


def _normalize_next(next_value: object) -> str:
    if not isinstance(next_value, str) or not next_value:
        return _DEFAULT_REDIRECT_PATH

    parsed = urlsplit(next_value)
    if parsed.scheme or parsed.netloc:
        return _DEFAULT_REDIRECT_PATH
    if not next_value.startswith("/") or next_value.startswith("//"):
        return _DEFAULT_REDIRECT_PATH
    return next_value


def _render_auth_template(
    request: Request,
    *,
    template_name: str,
    current_page: str,
    next_url: str,
    error_message: str | None = None,
    form_data: dict[str, object] | None = None,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    context: dict[str, object] = {
        "request": request,
        "current_user": None,
        "current_user_display_name": None,
    }
    context.update(
        {
            "current_page": current_page,
            "next_url": next_url,
            "error_message": error_message,
            "form_data": form_data or {},
            "google_oauth_enabled": settings.google_oauth_enabled,
            "hide_sidebar": True,
            "csrf_token": ensure_csrf_token(request),
        }
    )
    return templates.TemplateResponse(
        request,
        template_name,
        context,
        status_code=status_code,
    )


def _render_logout_error_template(
    request: Request,
    *,
    current_user: AuthUser | None,
    status_code: int = status.HTTP_403_FORBIDDEN,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "message.html",
        {
            "request": request,
            "current_user": current_user,
            "current_user_display_name": get_user_display_name(current_user),
            "hide_sidebar": True,
            "csrf_token": ensure_csrf_token(request),
            "title": "Не удалось выполнить выход",
            "message": csrf_error_message(),
            "details": "Обновите страницу, затем повторите попытку.",
            "message_type": "error",
            "primary_url": "/",
            "primary_text": "На главную",
            "primary_icon": "fa-home",
        },
        status_code=status_code,
    )


def _build_redirect_with_next(path: str, *, next_url: str) -> str:
    normalized_next = _normalize_next(next_url)
    if normalized_next == _DEFAULT_REDIRECT_PATH:
        return path
    return f"{path}?{urlencode({'next': normalized_next})}"


def _render_google_oauth_error_template(
    request: Request,
    details: str | None = None,
    *,
    next_url: str,
    title: str,
    message: str,
    status_code: int,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "message.html",
        {
            "request": request,
            "current_user": None,
            "current_user_display_name": None,
            "hide_sidebar": True,
            "csrf_token": ensure_csrf_token(request),
            "title": title,
            "message": message,
            "details": details,
            "message_type": "error",
            "primary_url": _build_redirect_with_next("/auth/login", next_url=next_url),
            "primary_text": "Ко входу",
            "primary_icon": "fa-right-to-bracket",
            "secondary_url": next_url,
            "secondary_text": "Продолжить без входа",
            "secondary_icon": "fa-arrow-right",
        },
        status_code=status_code,
    )


def _set_auth_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=settings.AUTH_SESSION_COOKIE_NAME,
        value=session_id,
        max_age=settings.AUTH_SESSION_MAX_AGE,
        httponly=True,
        samesite=settings.AUTH_SESSION_SAME_SITE,
        secure=settings.AUTH_SESSION_HTTPS_ONLY,
    )


def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.AUTH_SESSION_COOKIE_NAME,
        httponly=True,
        samesite=settings.AUTH_SESSION_SAME_SITE,
        secure=settings.AUTH_SESSION_HTTPS_ONLY,
    )


@router.get("/google/start")
async def google_start(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: AuthUser | None = Depends(get_current_user),
):
    next_url = _normalize_next(request.query_params.get("next"))
    if current_user is not None:
        return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)

    try:
        flow = auth_service.start_google_oauth_login(next_url=next_url)
    except OAuthConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        ) from exc

    request.session[_GOOGLE_OAUTH_UI_SESSION_KEY] = flow.session_payload
    return RedirectResponse(
        url=flow.authorization_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    oauth_session = request.session.pop(_GOOGLE_OAUTH_UI_SESSION_KEY, None)
    next_url = _DEFAULT_REDIRECT_PATH
    if isinstance(oauth_session, dict):
        next_url = _normalize_next(oauth_session.get("next"))

    try:
        result = await auth_service.complete_google_oauth_login(
            oauth_session=oauth_session,
            provided_state=request.query_params.get("state"),
            provider_error=request.query_params.get("error"),
            code=request.query_params.get("code"),
        )
    except OAuthConfigurationError:
        return _render_google_oauth_error_template(
            request,
            next_url=next_url,
            title="Вход через Google недоступен",
            message="Не удалось завершить вход через Google. Повторите попытку позже",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except OAuthStateInvalidError:
        return _render_google_oauth_error_template(
            request,
            next_url=next_url,
            title="Сессия входа истекла",
            message="Не удалось подтвердить запрос на вход через Google.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except OAuthProviderRejectedError:
        return _render_google_oauth_error_template(
            request,
            next_url=next_url,
            title="Не удалось войти через Google",
            message="Google отклонил запрос на вход.",
            details="Повторите попытку и подтвердите доступ к аккаунту.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except OAuthAuthorizationCodeMissingError:
        return _render_google_oauth_error_template(
            request,
            next_url=next_url,
            title="Не удалось войти через Google",
            message="Ответ Google не содержит кода авторизации.",
            details="Начните вход заново со страницы авторизации.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except OAuthProviderUnavailableError:
        return _render_google_oauth_error_template(
            request,
            next_url=next_url,
            title="Google временно недоступен",
            message="Не удалось завершить вход через Google.",
            details="Попробуйте снова через несколько минут.",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )
    except OAuthEmailNotVerifiedError:
        return _render_google_oauth_error_template(
            request,
            next_url=next_url,
            title="Email не подтвержден",
            message="Не удалось завершить вход через Google.",
            details="Google не подтвердил email этого аккаунта.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except (EmailAlreadyExistsError, OAuthIdentityAlreadyLinkedToAnotherUserError):
        return _render_google_oauth_error_template(
            request,
            next_url=next_url,
            title="Аккаунт уже используется",
            message="Не удалось завершить вход через Google.",
            details="Этот email или Google-аккаунт уже связан с другим способом входа.",
            status_code=status.HTTP_409_CONFLICT,
        )
    except UserIsInactiveError:
        return _render_google_oauth_error_template(
            request,
            next_url=next_url,
            title="Аккаунт недоступен",
            message="Этот пользовательский аккаунт отключен.",
            details="Обратитесь к администратору или используйте другой аккаунт.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    redirect = RedirectResponse(
        url=result.next_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )
    _set_auth_cookie(redirect, result.session_id)
    return redirect


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user: AuthUser | None = Depends(get_current_user),
):
    next_url = _normalize_next(request.query_params.get("next"))
    if current_user is not None:
        return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
    return _render_auth_template(
        request,
        template_name="auth/login.html",
        current_page="login",
        next_url=next_url,
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    current_user: AuthUser | None = Depends(get_current_user),
):
    next_url = _normalize_next(request.query_params.get("next"))
    if current_user is not None:
        return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
    return _render_auth_template(
        request,
        template_name="auth/register.html",
        current_page="register",
        next_url=next_url,
    )


@router.post(
    "/register",
    response_model=AuthUser,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: AuthUser | None = Depends(get_current_user),
):
    next_url = _normalize_next(request.query_params.get("next"))
    source, raw_payload = await read_request_payload(request)
    if current_user is not None:
        if source == "form":
            return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already authenticated",
        )

    if source == "form":
        try:
            validate_csrf(request, raw_payload.get("csrf_token"))
        except HTTPException as exc:
            return _render_auth_template(
                request,
                template_name="auth/register.html",
                current_page="register",
                next_url=_normalize_next(raw_payload.get("next")),
                error_message=csrf_error_message(),
                form_data={"email": raw_payload.get("email", "")},
                status_code=exc.status_code,
            )

    try:
        payload = AuthRegister.model_validate(raw_payload)
    except ValidationError as exc:
        if source == "json":
            raise RequestValidationError(exc.errors()) from exc
        return _render_auth_template(
            request,
            template_name="auth/register.html",
            current_page="register",
            next_url=_normalize_next(raw_payload.get("next")),
            error_message="Проверьте email и пароль: пароль должен быть длиной от 8 символов.",
            form_data={"email": raw_payload.get("email", "")},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = await auth_service.register(payload)
    except EmailAlreadyExistsError:
        if source == "json":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            ) from None
        return _render_auth_template(
            request,
            template_name="auth/register.html",
            current_page="register",
            next_url=_normalize_next(raw_payload.get("next")),
            error_message="Пользователь с таким email уже существует.",
            form_data={"email": payload.email},
            status_code=status.HTTP_409_CONFLICT,
        )

    session_id = await auth_service.login_create_session(user.id)
    if source == "form":
        redirect = RedirectResponse(
            url=_normalize_next(raw_payload.get("next")),
            status_code=status.HTTP_303_SEE_OTHER,
        )
        _set_auth_cookie(redirect, session_id)
        return redirect
    _set_auth_cookie(response, session_id)
    return user


@router.post("/login", response_model=AuthUser)
async def login(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: AuthUser | None = Depends(get_current_user),
):
    next_url = _normalize_next(request.query_params.get("next"))
    source, raw_payload = await read_request_payload(request)
    if current_user is not None:
        if source == "form":
            return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already authenticated",
        )

    if source == "form":
        try:
            validate_csrf(request, raw_payload.get("csrf_token"))
        except HTTPException as exc:
            return _render_auth_template(
                request,
                template_name="auth/login.html",
                current_page="login",
                next_url=_normalize_next(raw_payload.get("next")),
                error_message=csrf_error_message(),
                form_data={"email": raw_payload.get("email", "")},
                status_code=exc.status_code,
            )

    try:
        payload = AuthLogin.model_validate(raw_payload)
    except ValidationError as exc:
        if source == "json":
            raise RequestValidationError(exc.errors()) from exc
        return _render_auth_template(
            request,
            template_name="auth/login.html",
            current_page="login",
            next_url=_normalize_next(raw_payload.get("next")),
            error_message="Укажите корректный email и пароль.",
            form_data={"email": raw_payload.get("email", "")},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = await auth_service.authenticate(payload)
    if user is None:
        if source == "json":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return _render_auth_template(
            request,
            template_name="auth/login.html",
            current_page="login",
            next_url=_normalize_next(raw_payload.get("next")),
            error_message="Неверный email или пароль.",
            form_data={"email": raw_payload.get("email", "")},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    session_id = await auth_service.login_create_session(user.id)

    if source == "form":
        redirect = RedirectResponse(
            url=_normalize_next(raw_payload.get("next")),
            status_code=status.HTTP_303_SEE_OTHER,
        )
        _set_auth_cookie(redirect, session_id)
        return redirect
    _set_auth_cookie(response, session_id)
    return user


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    request: Request,
    response: Response,
    current_user: AuthUser = Depends(require_auth),
    auth_service: AuthService = Depends(get_auth_service),
):
    source, payload = await read_request_payload(request)
    if source == "form":
        try:
            validate_csrf(request, payload.get("csrf_token"))
        except HTTPException as exc:
            return _render_logout_error_template(
                request,
                current_user=current_user,
                status_code=exc.status_code,
            )

    session_id = request.cookies.get(settings.AUTH_SESSION_COOKIE_NAME)
    if session_id and current_user is not None:
        await auth_service.logout(session_id=session_id, user_id=current_user.id)

    if source == "form":
        redirect = RedirectResponse(
            url=_normalize_next(payload.get("next")),
            status_code=status.HTTP_303_SEE_OTHER,
        )
        _clear_auth_cookie(redirect)
        return redirect
    _clear_auth_cookie(response)
    return {"message": "Logged out"}
