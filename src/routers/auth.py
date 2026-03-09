import secrets
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from src.config import settings
from src.dependencies import get_auth_service, get_current_user
from src.exceptions import EmailAlreadyExistsError
from src.schemas import AuthLogin, AuthRegister, AuthUser
from src.services.auth import AuthService
from src.utils import ensure_csrf_token, get_user_display_name, templates

router = APIRouter(prefix="/auth", tags=["auth"])
_DEFAULT_REDIRECT_PATH = "/"
_JSON_CONTENT_TYPE = "application/json"
_FORM_CONTENT_TYPES = {
    "application/x-www-form-urlencoded",
    "multipart/form-data",
}


def _normalize_next(next_value: object) -> str:
    if not isinstance(next_value, str) or not next_value:
        return _DEFAULT_REDIRECT_PATH

    parsed = urlsplit(next_value)
    if parsed.scheme or parsed.netloc:
        return _DEFAULT_REDIRECT_PATH
    if not next_value.startswith("/") or next_value.startswith("//"):
        return _DEFAULT_REDIRECT_PATH
    return next_value


def _validate_csrf(request: Request, submitted_token: object) -> None:
    expected_token = request.session.get("csrf_token")
    if not isinstance(expected_token, str) or not expected_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token is missing",
        )
    if not isinstance(submitted_token, str) or not secrets.compare_digest(
        expected_token,
        submitted_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )


async def _read_request_payload(request: Request) -> tuple[str, dict[str, object]]:
    content_type = request.headers.get("content-type", "")
    media_type = content_type.split(";", 1)[0].strip().lower()

    if media_type == _JSON_CONTENT_TYPE:
        try:
            payload = await request.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed JSON body",
            ) from exc
        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON body must be an object",
            )
        return "json", payload

    if media_type in _FORM_CONTENT_TYPES:
        form = await request.form()
        return "form", dict(form)

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Unsupported Media Type",
    )


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


def _csrf_error_message() -> str:
    return "Сессия формы истекла или стала недействительной. Обновите страницу и попробуйте снова."


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
            "message": _csrf_error_message(),
            "details": "Обновите страницу, затем повторите попытку.",
            "message_type": "error",
            "primary_url": "/",
            "primary_text": "На главную",
            "primary_icon": "fa-home",
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
    source, raw_payload = await _read_request_payload(request)
    if current_user is not None:
        if source == "form":
            return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already authenticated",
        )

    if source == "form":
        try:
            _validate_csrf(request, raw_payload.get("csrf_token"))
        except HTTPException as exc:
            return _render_auth_template(
                request,
                template_name="auth/register.html",
                current_page="register",
                next_url=_normalize_next(raw_payload.get("next")),
                error_message=_csrf_error_message(),
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
    source, raw_payload = await _read_request_payload(request)
    if current_user is not None:
        if source == "form":
            return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already authenticated",
        )

    if source == "form":
        try:
            _validate_csrf(request, raw_payload.get("csrf_token"))
        except HTTPException as exc:
            return _render_auth_template(
                request,
                template_name="auth/login.html",
                current_page="login",
                next_url=_normalize_next(raw_payload.get("next")),
                error_message=_csrf_error_message(),
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


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    current_user: AuthUser | None = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    source, payload = await _read_request_payload(request)
    if source == "form":
        try:
            _validate_csrf(request, payload.get("csrf_token"))
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
