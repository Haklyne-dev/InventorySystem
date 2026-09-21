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
        name: $("#name").val(),
        email: $("#email").val(),
        password: $("#password").val()
    };
    $("#ob-account").fadeOut(500, function() {
        $("#ob-loading").fadeIn(500);
        $("#ob-loading").css("display", "block");
    });

    console.log("Registering new account...");
    $("#loading-text").text("Creating account...");

    $.ajax({
        url: "/api/auth/register",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            name: onboardingData.account.name,
            email: onboardingData.account.email,
            password: onboardingData.account.password,
            invite_code: "no-code"
        }),
        success: function(response) {
            console.log("Account created successfully:", response);
            logInUser(onboardingData);
        },
        error: function(xhr, status, error) {
            console.error("Error creating account:", error);
            alert("Error creating account: " + xhr.responseText);
            $("#ob-loading").fadeOut(500, function() {
                $("#ob-server").fadeIn(500);
                $("#ob-server").css("display", "block");
            });
        }
    });
});

function logInUser(onboardingData) {
    $("#loading-text").text("Logging in...");
    $.ajax({
        url: "/api/auth/login",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ email: onboardingData.account.email, password: onboardingData.account.password }),
        success: function(response) {
            console.log("Logged in successfully:", response);
            // Placeholder for server configuration
            $("#ob-loading").fadeOut(500, function() {
                $("#ob-complete").fadeIn(500);
                $("#ob-complete").css("display", "block");
            });
        },
        error: function(xhr, status, error) {
            console.error("Error logging in:", error);
            alert("Error logging in: " + xhr.responseText);
        }
    });
}

$(document).ready(function() {
    $.ajax({
        url: "/api/onboarding/status",
        method: "GET",
        success: function(response) {
            if (response.onboarded) {
                window.location.href = "/";
            } else {
                $(".onboarding-container").fadeIn(500);
                $("#ob-welcome").fadeIn(500);
                $("#ob-welcome").css("display", "block");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error checking onboarding status:", error);
            alert("Error checking onboarding status: " + xhr.responseText);
        }
    });
});