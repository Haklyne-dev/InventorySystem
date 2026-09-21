// Helper to clear local cookies if any non-HttpOnly fallbacks exist, 
// though the backend will handle the official HttpOnly token removal.
function clearLocalCookie() {
    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

const currentPath = window.location.pathname;

if (currentPath === "/login" || currentPath === "/register") {
    // 1. Instead of checking getCookie(), proactively ask the backend if we are logged in.
    $.ajax({
        url: "/api/auth/me",
        method: "GET",
        xhrFields: { withCredentials: true },
        success: function (data) {
            window.location.href = "/";
        },
        error: function () {
            document.body.classList.remove('loading');
        }
    });

    if (currentPath === "/login") {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get("registered") === "true") {
            $("#message").text("Registration successful! Please log in.").addClass("success");
        }
        if (urlParams.get("error") === "true") {
            $("#message").text("Invalid email or password. Please try again.").addClass("error");
        }

        $("#login-form").submit(function (e) {
            e.preventDefault();
            var email = $("#email").val();
            var password = $("#password").val();

            $.ajax({
                url: "/api/auth/login",
                method: "POST",
                xhrFields: { withCredentials: true },
                contentType: "application/json",
                data: JSON.stringify({ email: email, password: password }),
                success: function (data) {
                    window.location.href = "/";
                },
                error: function () {
                    window.location.href = "/login?error=true";
                }
            });
        });
    } else {
        $("#register-form").submit(function (e) {
            e.preventDefault();
            var name = $("#name").val();
            var email = $("#email").val();
            var password = $("#password").val();
            var code = $("#code").val();

            $.ajax({
                url: "/api/auth/register",
                method: "POST",
                xhrFields: { withCredentials: true },
                contentType: "application/json",
                data: JSON.stringify({
                    name: name,
                    email: email,
                    password: password,
                    invite_code: code
                }),
                success: function (data) {
                    window.location.href = "/login?registered=true";
                },
                error: function () {
                    alert("Error registering user");
                }
            });
        });
    }
} 
else if (currentPath === "/logout") {
    $.ajax({
        url: "/api/auth/logout",
        method: "POST",
        xhrFields: { withCredentials: true },
        success: function () {
            clearLocalCookie();
            window.location.href = "/login";
        },
        error: function () {
            clearLocalCookie();
            window.location.href = "/login";
        }
    });
}
else {
    $.ajax({
        url: "/api/auth/me",
        method: "GET",
        xhrFields: { withCredentials: true },
        success: function (data) {
            emitAuthTrigger({ user: data });
            document.body.classList.remove('loading');
        },
        error: function () {
            clearLocalCookie();
            window.location.href = "/login";
        }
    });
}
