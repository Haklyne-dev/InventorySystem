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
                const fuse = new Fuse(data, {
                    keys: ['name', 'description', 'category', 'location'],
                    threshold: 0.3
                });
                const filteredParts = fuse.search(searchQuery);
                console.log(filteredParts);
                filteredParts.forEach(part => {
                    item = part.item;
                    partsTbody.append(`
                        <tr>
                            <td>${item.id}</td>
                            <td><a href="/parts/${item.id}">${item.name}</a></td>
                            <td>${item.quantity}</td>
                            <td>${item.location}</td>
                        </tr>
                    `);
                });
            }
        });
    }
});