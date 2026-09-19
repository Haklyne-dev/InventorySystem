var onboardingData = {
    account: {},
    server: {}
};


$("#start-onboarding").on("click", function() {
    $("#ob-welcome").fadeOut(500, function() {
        $("#ob-account").fadeIn(500);
        $("#ob-account").css("display", "block");
    });
});

$("#account-form").on("submit", function(event) {
    event.preventDefault();
    onboardingData.account = {
        username: $("#account-username").val(),
        email: $("#account-email").val(),
        password: $("#account-password").val()
    };
    $("#ob-account").fadeOut(500, function() {
        $("#ob-server").fadeIn(500);
        $("#ob-server").css("display", "block");
    });
});

$("#server-form").on("submit", function(event) {
    event.preventDefault();
    onboardingData.server = {
        serverName: $("#server-name").val(),
        autoUpdate: $("#auto-update").is(":checked")
    };
    $("#ob-server").fadeOut(500, function() {
        $("#ob-loading").fadeIn(500);
        $("#ob-loading").css("display", "block");
    });
});