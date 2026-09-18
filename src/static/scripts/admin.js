window.addEventListener('auth-trigger', (event) => {
    const user = event.detail.user;
    if (user) {
        if (user.role !== "admin") {
            window.location.href = "/";
        }
        $.ajax({
            url: "/api/users_full",
            method: "GET",
            xhrFields: {
                withCredentials: true
            },
            success: function (users) {
                const userList = $("#users-list");
                users.forEach(function (user) {
                    const userItem = $("<tr></tr>");
                    userItem.append(`<td>${user.id}</td>`);
                    userItem.append(`<td>${user.name}</td>`);
                    userItem.append(`<td>${user.email}</td>`);
                    userItem.append(`<td>${user.role}</td>`);
                    userItem.append(`<td class="btn-group"><button class="btn btn-primary" onclick="viewProfile(${user.id})">View Profile</button><button class="btn btn-danger" onclick="deleteUser(${user.id})">Delete</button></td>`);
                    userList.append(userItem);
                });
            }
        });
    }
});

$(document).ready(function () {
    aciveTab = $(".tab-link.active").data("tab");
    $(".tab-content").hide();
    $("#" + aciveTab).show();
});

$(".tab-link").on("click", function () {
    $(".tab-link").removeClass("active");
    $(this).addClass("active");
    $(".tab-content").hide();
    const target = $(this).data("tab");
    $("#" + target).show();
});

function deleteUser(userId) {
    if (confirm("Are you sure you want to delete this user? This action cannot be undone.")) {
        $.ajax({
            url: `/api/auth/${userId}`,
            type: 'DELETE',
            xhrFields: {
                withCredentials: true
            },
            success: function (response) {
                window.location.reload();
            },
            error: function (xhr, status, error) {
                console.error('Error deleting user:', error);
            }
        });
    }
};

function viewProfile(userId) {
    window.location.href = `/profile/${userId}`;
}