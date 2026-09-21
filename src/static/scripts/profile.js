window.addEventListener('auth-trigger', (event) => {
    const user = event.detail.user;
    if (user) {
        const urlID = window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1);
        if (urlID == user.id) {
            displayUserProfile(user, true);
        }
        else {
            if (user.role == "admin") {
                $.ajax({
                    url: "/api/users/" + urlID + "/full",
                    method: "GET",
                    xhrFields: {
                        withCredentials: true
                    },
                    success: function (userData) {
                        var isCurrentUser = (user.id === userData.id);
                        displayUserProfile(userData, isCurrentUser);
                    }
                });
            }
            else {
                $.ajax({
                    url: "/api/users/" + urlID,
                    method: "GET",
                    xhrFields: {
                        withCredentials: true
                    },
                    success: function (userData) {
                        var isCurrentUser = (user.id === userData.id);
                        displayUserProfile(userData, isCurrentUser);
                    }
                });
            }
        }

    }
});

function displayUserProfile(user, isCurrentUser = false) {
    $("#profile-name").text(user.name);
    if (user.email) {
        $("#profile-info").append(`<p>Email: ${user.email}</p>`);
        $("#profile-info").append(`<p>Role: ${user.role}</p>`);

        $.ajax({
            url: "/api/api_keys/user/" + user.id,
            method: "GET",
            xhrFields: {
                withCredentials: true
            },
            success: function (apiKeysData) {
                $.each(apiKeysData, function (index, apiKey) {
                    let timestamp = new Date(apiKey.created_at);
                    let formattedTimestamp = timestamp.toLocaleString();
                    apiKey.created_at = formattedTimestamp;
                    $("#api-keys").append(`<tr id="key-${apiKey.id}">
                    <td>${apiKey.name}</td>
                    <td>${apiKey.created_at}</td>
                    <td><button class="btn btn-danger" onclick="deleteApiKey('${apiKey.id}')">Delete</button></td>
                </tr>`);
                });
            }
        });

        $("#api-keys-section").show();
    }
    if (isCurrentUser) {
        $("#generate-api-key").show();
    }
    
    let avatarUrl = "/images/avatar/" + user.id;
    $("#profile-image").attr("src", avatarUrl);

    $.ajax({
        url: "/api/users/" + user.id + "/history",
        method: "GET",
        xhrFields: {
            withCredentials: true
        },
        success: function (historyData) {
            $.each(historyData, function (index, activity) {
                let timestamp = new Date(activity.created_at);
                let formattedTimestamp = timestamp.toLocaleString();
                activity.created_at = formattedTimestamp;
                $("#activity-history").append(`<tr>
                    <td>${activity.type}</td>
                    <td><a href="/parts/${activity.part_id}">${activity.part_id}</a></td>
                    <td>${activity.created_at}</td>
                    <td>${activity.note}</td>
                    </tr>`);
            });
        }
    });
}

$("#generate-api-key").click(function () {
    $("#api-key-popup").show();
    $("#api-key-details").html(`
        <form id='api-key-form'>
            <label for='api-key-name'>API Key Name:</label>
            <input type='text' id='api-key-name' name='api-key-name' required>
            <button type='submit'>Generate</button>
        </form>`);

    $("#api-key-form").submit(function (event) {
        event.preventDefault();
        const apiKeyName = $("#api-key-name").val();
        $.ajax({
            url: "/api/api_keys/create",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ name: apiKeyName }),
            xhrFields: {
                withCredentials: true
            },
            success: function (newApiKey) {
                let timestamp = new Date(newApiKey.created_at);
                let formattedTimestamp = timestamp.toLocaleString();
                newApiKey.created_at = formattedTimestamp;
                $("#api-keys").append(`<tr id="key-${newApiKey.id}">
                    <td>${newApiKey.name}</td>
                    <td>${newApiKey.created_at}</td>
                    <td><button class="btn btn-danger" onclick="deleteApiKey('${newApiKey.id}')">Delete</button></td>
                </tr>`);
                $("#api-key-name").val("");
                $("#api-key-details").html(`
                    <h3 class="success">API Key Generated Successfully!</h3>
                    <p>New API Key:</p>
                    <pre>${newApiKey.key}<button id="copy-api-key" onclick="copyToClipboard('${newApiKey.key}')">Copy</button></pre>
                    <p class="warning">Please copy and save this key securely. You won't be able to see it again.</p>
                `);
            },
            error: function () {
                alert("Failed to generate API key.");
            }
        });
    });
});

function deleteApiKey(apiKeyId) {
    if (confirm("Are you sure you want to delete this API key?")) {
        $.ajax({
            url: "/api/api_keys/" + apiKeyId,
            method: "DELETE",
            xhrFields: {
                withCredentials: true
            },
            success: function () {
                $("#key-" + apiKeyId).remove();
            },
            error: function () {
                alert("Failed to delete API key.");
            }
        });
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function () {
        $("#copy-api-key").text("Copied!");
        window.setTimeout(function () {
            $("#copy-api-key").text("Copy");
        }, 2000);
    }, function (err) {
        console.error("Could not copy text: ", err);
    });
}