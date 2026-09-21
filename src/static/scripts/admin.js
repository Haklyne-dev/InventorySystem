window.addEventListener('auth-trigger', (event) => {
    const user = event.detail.user;
    if (user) {
        if (user.role !== "admin") {
            window.location.href = "/";
        }

        selectTab(window.location.hash.substring(1) || "parts");

        var allUsers = [];

        $.ajax({
            url: "/api/users_full",
            method: "GET",
            xhrFields: {
                withCredentials: true
            },
            success: function (users) {
                allUsers = users;
                const userList = $("#users-list");
                users.forEach(function (user) {
                    const userItem = $("<tr></tr>");
                    userItem.append(`<td>${user.id}</td>`);
                    userItem.append(`<td><a href="/profile/${user.id}">${user.name}</a></td>`);
                    userItem.append(`<td>${user.email}</td>`);
                    userItem.append(`<td>${user.role}</td>`);
                    userItem.append(`<td class="btn-group"><button class="btn btn-danger" onclick="deleteUser(${user.id})">Delete</button></td>`);
                    userList.append(userItem);
                });
            }
        });

        $.ajax({
            url: "/api/parts",
            method: "GET",
            xhrFields: {
                withCredentials: true
            },
            success: function (parts) {
                const partsList = $("#parts-list");
                parts.forEach(function (part) {
                    const partItem = $("<tr></tr>");
                    partItem.append(`<td>${part.id}</td>`);
                    partItem.append(`<td><a href="/parts/${part.id}">${part.name}</a></td>`);
                    partItem.append(`<td class="btn-group"><button class="btn btn-danger" onclick="deletePart(${part.id})">Delete</button></td>`);
                    partsList.append(partItem);
                });
            }
        });

        $.ajax({
            url: "/api/api_keys",
            method: "GET",
            xhrFields: {
                withCredentials: true
            },
            success: function (apiKeys) {
                const apiKeysList = $("#api-keys-list");
                apiKeys.forEach(function (apiKey) {
                    let user = allUsers.find(u => u.id === apiKey.user_id);
                    let timestamp = new Date(apiKey.created_at);
                    apiKey.created_at = timestamp.toLocaleString();
                    const apiKeyItem = $("<tr></tr>");
                    apiKeyItem.append(`<td>${apiKey.id}</td>`);
                    apiKeyItem.append(`<td>${apiKey.name}</td>`);
                    apiKeyItem.append(`<td>${apiKey.created_at}</td>`);
                    apiKeyItem.append(`<td><a href="/profile/${user ? user.id : 'unknown'}">${user ? user.name : 'Unknown'}</a></td>`);
                    apiKeyItem.append(`<td class="btn-group"><button class="btn btn-danger" onclick="deleteApiKey(${apiKey.id})">Delete</button></td>`);
                    apiKeysList.append(apiKeyItem);

                    apiKey.api_events.forEach(function (event) {
                        const apiEventsList = $("#api-usage-list");
                        const eventItem = $("<tr></tr>");
                        let eventTimestamp = new Date(event.created_at);
                        event.created_at = eventTimestamp.toLocaleString();
                        eventItem.append(`<td>${event.created_at}</td>`);
                        eventItem.append(`<td>${event.api_key_id}</td>`);
                        eventItem.append(`<td>${event.endpoint}</td>`);
                        eventItem.append(`<td>${event.origin_ip}</td>`);
                        eventItem.append(`<td>${event.method}</td>`);
                        eventItem.append(`<td>${event.status_code}</td>`);
                        apiEventsList.append(eventItem);
                    });
                });
            }
        });

        $.ajax({
            url: "/api/auth/invite_codes",
            method: "GET",
            xhrFields: {
                withCredentials: true
            },
            success: function (inviteCodes) {
                const inviteCodesList = $("#invite-codes-list");
                inviteCodes.forEach(function (inviteCode) {
                    let timestamp = new Date(inviteCode.expires_at);
                    inviteCode.expires_at = timestamp.toLocaleString();
                    const inviteCodeItem = $("<tr></tr>");
                    inviteCodeItem.append(`<td>${inviteCode.code}</td>`);
                    inviteCodeItem.append(`<td>${inviteCode.role}</td>`);
                    inviteCodeItem.append(`<td>${inviteCode.user_amount}</td>`);
                    inviteCodeItem.append(`<td>${inviteCode.used}</td>`);
                    inviteCodeItem.append(`<td>${inviteCode.expires_at}</td>`);
                    inviteCodeItem.append(`<td class="btn-group"><button class="btn btn-danger" onclick="deleteInviteCode(${inviteCode.id})">Delete</button></td>`);
                    inviteCodesList.append(inviteCodeItem);
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
    const tabName = $(this).data("tab");
    selectTab(tabName);
});

function selectTab(tabName) {
    $(".tab-link").removeClass("active");
    $(`.tab-link[data-tab="${tabName}"]`).addClass("active");
    $(".tab-content").hide();
    $("#" + tabName).show();
    window.location.hash = tabName; 
}

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

function deletePart(partId) {
    if (confirm("Are you sure you want to delete this part? This action cannot be undone.")) {
        $.ajax({
            url: `/api/parts/${partId}`,
            type: 'DELETE',
            xhrFields: {
                withCredentials: true
            },
            success: function (response) {
                window.location.reload();
            },
            error: function (xhr, status, error) {
                console.error('Error deleting part:', error);
            }
        });
    }
};

function deleteApiKey(apiKeyId) {
    if (confirm("Are you sure you want to delete this API key? This action cannot be undone.")) {
        $.ajax({
            url: `/api/api_keys/${apiKeyId}`,
            type: 'DELETE',
            xhrFields: {
                withCredentials: true
            },
            success: function (response) {
                window.location.reload();
            },
            error: function (xhr, status, error) {
                console.error('Error deleting API key:', error);
            }
        });
    }
};

function generateInviteCode() {
    const popup = $("#invite-code-popup");
    const content = $("#invite-code-details");
    content.html(`
        <form id="invite-code-form">
            <label for="role">Select Role:</label>
            <select id="role" name="role">
                <option value="member">Member</option>
                <option value="admin">Admin</option>
            </select>
            <label for="user_amount">Number of Users:</label>
            <input type="number" id="user_amount" name="user_amount" min="1" value="1" required>
            <button type="submit">Generate Invite Code</button>
        </form>
        `);

    $("#invite-code-form").on("submit", function (e) {
        e.preventDefault();
        const role = $("#role").val();
        const user_amount = parseInt($("#user_amount").val(), 10);
        $.ajax({
            url: `/api/auth/invite`,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ role: role, user_amount: user_amount }),
            xhrFields: {
                withCredentials: true
            },
            success: function (response) {
                content.html(`
                    <h3 class="success">Invite Code Generated</h3>
                    <p>Generated Invite Code: </p>
                    <pre>${response.code}<button id="copy-code" onclick="copyToClipboard('${response.code}')">Copy</button></pre>
                    <p>Expires At: ${new Date(response.expires_at).toLocaleString()}</p>
                    `);
                $("#invite-codes-list").append(`<tr>
                    <td>${response.code}</td>
                    <td>${response.role}</td>
                    <td>${response.user_amount}</td>
                    <td>${response.used}</td>
                    <td>${new Date(response.expires_at).toLocaleString()}</td>
                    <td class="btn-group"><button class="btn btn-danger" onclick="deleteInviteCode(${response.id})">Delete</button></td>
                </tr>`);
            },
            error: function (xhr, status, error) {
                console.error('Error generating invite code:', error);
            }
        });
    });
    popup.show();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function () {
        $("#copy-code").text("Copied!");
        window.setTimeout(function () {
            $("#copy-code").text("Copy");
        }, 2000);
    }, function (err) {
        console.error("Could not copy text: ", err);
    });
}

function deleteInviteCode(inviteCodeId) {
    if (confirm("Are you sure you want to delete this invite code? This action cannot be undone.")) {
        $.ajax({
            url: `/api/auth/invite_codes/${inviteCodeId}`,
            type: 'DELETE',
            xhrFields: {
                withCredentials: true
            },
            success: function (response) {
                window.location.reload();
            },
            error: function (xhr, status, error) {
                console.error('Error deleting invite code:', error);
            }
        });
    }
};