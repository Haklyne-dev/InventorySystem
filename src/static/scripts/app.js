function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${value}; expires=${expires}; path=/`;
}

document.body.classList.add('loading');

window.addEventListener('auth-trigger', (event) => {
    const user = event.detail.user;
    if (user) {
        document.body.classList.remove('loading');
        $("#user-name").text(user.name);
        $("#user-email").text(user.email);
        $.ajax({
            url: "/api/users/" + user.id + "/avatar",
            method: "GET",
            xhrFields: {
                withCredentials: true
            },
            success: function (data) {
                var avatarUrl = "data:image/png;base64," + data.image;
                $("#user-avatar").attr("src", avatarUrl);
            },
            error: function () {
                // Handle profile update error
            }
        });

        if (user.role === "admin") {
            if ($("#admin-link").length) {
                $("#admin-link").show();
            }
        }
    } else {
        window.location.href = "/login";
    }
});

$(document).ready(function () {
    $("#user-avatar").on("click", function (e) {
        e.stopPropagation();
        $("#profile-dropdown").toggle();
    });

    $(document).on("click", function () {
        $("#profile-dropdown").hide();
    });

    $("#profile-dropdown").on("click", function (e) {
        e.stopPropagation();
    });

    $("#logout-link").on("click", function (e) {
        e.preventDefault();
        window.location.href = "/logout";
    });
});

function emitAuthTrigger(data) {
    const event = new CustomEvent('auth-trigger', { detail: data });
    window.dispatchEvent(event);
}

$("#search-button").on("click", function () {
    const searchQuery = $("#search-input").val();
    if (searchQuery.trim() !== "") {
        window.location.href = `/search?q=${encodeURIComponent(searchQuery)}`;
    }
});

$(".close").on("click", function () {
    $(".popup").hide();
});

window.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        const searchQuery = $("#search-input").val();
        if (searchQuery.trim() !== "" && $("#search-input").is(":focus")) {
            window.location.href = `/search?q=${encodeURIComponent(searchQuery)}`;
        }
    }
});