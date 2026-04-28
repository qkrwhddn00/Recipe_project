document.getElementById("mylabel_link").addEventListener("click", function(event) {
    if ("{{ GLOBAL_NICKNAME }}" === "게스트") {
        event.preventDefault();
        showModal();
    }
});

function showModal() {
    document.getElementById("error-modal").style.display = "block";
}

function closeModal() {
    document.getElementById("error-modal").style.display = "none";
}
