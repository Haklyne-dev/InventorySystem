var categories = [];

window.addEventListener('auth-trigger', (event) => {
    const user = event.detail.user;
    if (user) {
        if (user.role !== "admin") {
            window.location.href = "/";
        }
        const urlParams = new URLSearchParams(window.location.search);
        const partId = urlParams.get("id");
        if (partId) {
            $.ajax({
                url: `/api/parts/${partId}`,
                method: "GET",
                xhrFields: {
                    withCredentials: true
                },
                success: (partData) => {
                    $("#part-name").val(partData.name);
                    $("#part-quantity").val(partData.quantity);
                    $("#part-location").val(partData.location);
                    $("#category").val(partData.category);
                    $("#part-description").val(partData.description);
                    $("#part-number").val(partData.part_number);

                    // Populate vendor links
                    $(".vendor-link").remove();
                    partData.vendor_links.forEach(link => {
                        const newLinkDiv = document.createElement("div");
                        newLinkDiv.classList.add("vendor-link");
                        newLinkDiv.innerHTML = `
                            <input type="text" name="vendor_name[]" value="${link.name}" required />
                            <input type="url" name="vendor_url[]" value="${link.url}" required />
                            <button type="button" onclick="removeVendorLink(this)">Remove</button>
                        `;
                        if ($(".vendor-link").length === 0) {
                            newLinkDiv.querySelector("button").classList.add("disabled");
                        }
                        $("#new-vendor-button").before(newLinkDiv);
                    });
                }
            });
        }
        $(".create-part-form").on("submit", function (e) {
            e.preventDefault();
            const partData = {
                name: $("#part-name").val(),
                quantity: parseInt($("#part-quantity").val()),
                location: $("#part-location").val(),
                category: $("#category").val(),
                description: $("#part-description").val(),
                part_number: $("#part-number").val(),
                vendor_links: Array.from(document.querySelectorAll(".vendor-link")).map(linkDiv => {
                    const name = linkDiv.querySelector("input[name='vendor_name[]']").value;
                    const url = linkDiv.querySelector("input[name='vendor_url[]']").value;
                    return { name, url };
                })
            };

            console.log("Part data to be sent:", partData); // Log the part data before sending

            $.ajax({
                url: `/api/parts/${partId}/update`,
                method: "POST",
                contentType: "application/json",
                xhrFields: {
                    withCredentials: true
                },
                data: JSON.stringify(partData),
                success: function (response) {
                    $("#response-message").text("Part updated successfully!").show();
                    $("#response-message").removeClass("error");
                    $("#response-message").addClass("success");
                    setTimeout(() => {
                        $("#response-message").hide();
                        window.location.href = `/parts/${response.id}`;
                    }, 1000);

                },
                error: function (xhr, status, error) {
                    console.error("Error creating part:", error);
                    $("#response-message").text("Error creating part: " + xhr.responseJSON.detail).show();
                    $("#response-message").removeClass("success");
                    $("#response-message").addClass("error");
                }
            });
        });
        $.ajax({
            url: "/api/parts",
            method: "GET",
            xhrFields: {
                withCredentials: true
            },
            success: (data) => {
                categories = [...new Set(data.map(part => part.category))];
            }
        })
    }
});

const inputBox = document.getElementById("category");
const resultBox = document.getElementById("suggestions-box");

inputBox.addEventListener("keyup", () => {
    let input = inputBox.value;

    if (input.length === 0) {
        resultBox.innerHTML = "";
        return;
    }

    const filtered = categories.filter(item =>
        item.toLowerCase().includes(input.toLowerCase())
    );

    resultBox.innerHTML = filtered.map(item =>
        `<li onclick="selectInput('${item}')">${item}</li>`
    ).join("");
});

inputBox.addEventListener("focus", () => {
    resultBox.style.display = "block";
});

inputBox.addEventListener("blur", () => {
    window.setTimeout(() => {
        resultBox.style.display = "none";
    }, 350);
});

function selectInput(value) {
    inputBox.value = value;
    resultBox.innerHTML = "";
}

function addVendorLink() {

    const newLinkDiv = document.createElement("div");
    newLinkDiv.classList.add("vendor-link");
    newLinkDiv.innerHTML = `
        <input type="text" name="vendor_name[]" placeholder="Vendor Name" required />
        <input type="url" name="vendor_url[]" placeholder="Vendor URL" required />
        <button type="button" onclick="removeVendorLink(this)">Remove</button>
    `;
    
    $("#new-vendor-button").before(newLinkDiv);
}

function removeVendorLink(button) {
    const linkDiv = button.parentElement;
    linkDiv.remove();
}