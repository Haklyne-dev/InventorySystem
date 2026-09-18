window.addEventListener('auth-trigger', (event) => {
    const user = event.detail.user;
    if (user) {
        const queryParams = new URLSearchParams(window.location.search);
        const searchQuery = queryParams.get('q');

        $("#search-input").val(searchQuery);

        $.ajax({
            url: `/api/parts`,
            type: 'GET',
            xhrFields: {
                withCredentials: true
            },
            success: (data) => {
                const partsTbody = $("#parts-tbody");
                partsTbody.empty();
                const filteredParts = data.filter(part => {
                    return part.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        part.id.toString().includes(searchQuery) ||
                        part.category.toLowerCase().includes(searchQuery.toLowerCase());
                });
                filteredParts.forEach(part => {
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
    }
});