(function() {
    function parseNonNegativeInt(value, fallback = 0) {
        const parsed = Number.parseInt(String(value), 10);
        return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
    }

    window.habitFlowUtils = Object.assign({}, window.habitFlowUtils, {
        parseNonNegativeInt,
    });
})();
