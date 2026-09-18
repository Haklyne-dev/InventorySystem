window.addEventListener('auth-trigger', (event) => {
    const user = event.detail.user;
    if (user) {
        $.ajax({
            url: "/api/parts",
            method: "GET",
            xhrFields: {
                withCredentials: true
            },
            success: (data) => {
                const partsTbody = $("#parts-tbody");
                partsTbody.empty();
                data.forEach((part) => {
                    partsTbody.append(`
                        <tr>
                            <td>${part.id}</td>
                            <td><a href="/parts/${part.id}">${part.name}</a></td>
                            <td>${part.quantity}</td>
                            <td>${part.location}</td>
                        </tr>
                    `);
                });
            }
        });

        $("#download-labels-button").on("click", function () {
            $.ajax({
                url: "/api/downloads/label_sheet",
                method: "GET",
                xhrFields: {
                    withCredentials: true
                },
                xhrFields: {
                    withCredentials: true
                },
                success: function (response) {
                    blob = new Blob([response], { type: 'application/pdf' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'label_sheet.pdf';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                }
            });
        });
    }
});