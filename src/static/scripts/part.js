window.addEventListener('auth-trigger', (event) => {
    const user = event.detail.user;
    if (user) {
        const urlID = window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1);
        $.ajax({
            url: `/api/parts/${urlID}`,
            type: 'GET',
            xhrFields: {
                withCredentials: true
            },
            xhrFields: {
                withCredentials: true
            },
            success: (data) => {
                // Handle successful response
                $('#part-name').text(data.name);
                $('#part-id').text(data.id);
                $('#part-quantity').text(data.quantity);
                $('#part-location').text(data.location);
                $('#part-category').text(data.category);
                $('#part-description').html("<strong>Description:</strong><br> " + data.description);

                $.each(data.history, function (index, historyItem) {
                    $.ajax({
                        url: `/api/users/${historyItem.user_id}`,
                        type: 'GET',
                        xhrFields: {
                            withCredentials: true
                        },
                        xhrFields: {
                            withCredentials: true
                        },
                        success: (userData) => {
                            historyItem.actionUser = userData;
                            let timestamp = new Date(historyItem.created_at);
                            let formattedDate = timestamp.toLocaleString();
                            historyItem.created_at = formattedDate;
                            var historyEntry = `<tr>
                        <td>${historyItem.type}</td>
                        <td>${historyItem.created_at}</td>
                        <td>${historyItem.note}</td>
                        <td><a href="/profile/${historyItem.user_id}">${userData.name}</a></td>
                    </tr>`;
                            $('#part-history').append(historyEntry);
                        }
                    });
                });
            },
            error: (xhr, status, error) => {
                console.error('Error fetching part details:', error);
            }
        });

        $.ajax({
            url: `/api/parts/${urlID}/qr`,
            type: 'GET',
            xhrFields: {
                withCredentials: true
            },
            xhrFields: {
                withCredentials: true
            },
            success: (data) => {
                var codeUrl = "data:image/png;base64," + data.image;
                $("#part-qr").attr("src", codeUrl);
            }
        });
    }
});