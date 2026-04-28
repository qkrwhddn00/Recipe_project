document.addEventListener("DOMContentLoaded", function () {
            let errorContainer = document.getElementById("errorMessages");
            let errorMessage = errorContainer.getAttribute("data-messages").trim();

            if (errorMessage) {
                showModal(errorMessage);
            }
        });

        function showModal(message) {
            document.getElementById("modalMessage").textContent = message;
            document.getElementById("errorModal").style.display = "block";
        }

        function closeModal() {
            document.getElementById("errorModal").style.display = "none";
        }