document.addEventListener("DOMContentLoaded", function () {
            const form = document.querySelector("form");
            const ingredientInput = document.getElementById("ingredientInput");
            const modal = document.getElementById("warningModal");
            const modalContent = document.querySelector(".modal-content");
            const closeButton = document.getElementById("closeButton");

            // 페이지 로드 시 모달 숨기기
            modal.style.display = "none";

            // 폼 제출 시 재료 입력값 확인
            form.addEventListener("submit", function (event) {
                let inputValue = ingredientInput.value.trim();

                if (inputValue.length < 3) {
                    event.preventDefault(); // 폼 제출 방지
                    modal.style.display = "flex"; // 모달 표시
                    modal.style.justifyContent = "center"; // 가운데 정렬
                    modal.style.alignItems = "center";
                    modalContent.style.transform = "translate(-50%, -50%)"; // 정렬 보정
                    modalContent.style.position = "fixed"; // 중앙 고정
                    modalContent.style.top = "50%";
                    modalContent.style.left = "50%";
                }
            });

            // 모달 닫기 함수
            function closeModal() {
                modal.style.display = "none"; // "warningModal" 닫기
                ingredientInput.focus(); // 입력 필드로 포커스 이동
            }

            // "다시 시도" 버튼 클릭 시 모달 닫기
            closeButton.addEventListener("click", function () {
                modal.style.display = "none"; // "warningModal" 닫기
                ingredientInput.focus(); // 입력 필드로 포커스 이동
            });

            // 모달 바깥을 클릭하면 닫힘
            modal.addEventListener("click", function (event) {
                if (event.target === modal) {
                    closeModal();
                }
            });
        });