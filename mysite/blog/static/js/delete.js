document.addEventListener("DOMContentLoaded", function () {
    const deleteSelectedBtn = document.getElementById("deleteSelected");
    const deleteAllBtn = document.getElementById("deleteAll");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    // 선택 삭제 기능 구현
    deleteSelectedBtn.addEventListener("click", function () {
        let selectedIds = [];
        document.querySelectorAll(".recipe-checkbox:checked").forEach((checkbox) => {
            selectedIds.push(checkbox.value);
        });

        console.log("🔍 선택된 레시피 ID 배열:", selectedIds); // 콘솔에서 확인

        if (selectedIds.length === 0) {
            alert("삭제할 레시피를 선택하세요!");
            return;
        }

        fetch(deleteSelectedBtn.getAttribute("data-url"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ selected_ids: selectedIds }),
        })
            .then(response => response.json())
            .then(data => {
                console.log("🔍 서버 응답:", data); // 서버 응답 확인
                if (data.status === "success") {
                    alert("선택한 레시피가 삭제되었습니다.");
                    window.location.reload();
                } else {
                    alert("삭제 실패: " + data.message);
                }
            })
            .catch(error => console.error("오류 발생:", error));
    });

    // 전체 삭제 기능 구현
    deleteAllBtn.addEventListener("click", function () {
        if (!confirm("정말로 전체 삭제를 하시겠습니까?")) {
            return;
        }

        fetch(deleteAllBtn.getAttribute("data-url"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ action: "delete_all" }),
        })
            .then(response => response.json())
            .then(data => {
                console.log("🔍 서버 응답:", data); // 서버 응답 확인
                if (data.status === "success") {
                    alert("모든 레시피가 삭제되었습니다.");
                    window.location.reload();
                } else {
                    alert("삭제 실패: " + data.message);
                }
            })
            .catch(error => console.error("오류 발생:", error));
    });
});