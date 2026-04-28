    // 텍스트 포맷팅 함수
    function formatText(element) {
        const text = element.textContent.trim();
    
        // 텍스트를 마침표 기준으로 나누고, 필요 없는 문자 제거 후 배열로 저장
        let sentences = text.split('.').map(sentence =>
            sentence.replace(/", "/g, '').replace(/"/g, '').replace(/[,\[\]]/g, '').trim()
        ).filter(sentence => sentence !== '');
    
        // 기존 내용을 지운 후, 새로운 <p> 태그로 번호를 붙여 출력
        element.innerHTML = '';
    
        sentences.forEach((sentence, index) => {
            if (sentence) { // 빈 문자열이 아닐 때만 추가
                const paragraph = document.createElement('p');
                paragraph.textContent = `${index + 1}. ${sentence}.`; // 번호 추가
                element.appendChild(paragraph);
            }
        });
    }
    

    // 모달 열기
    function openModal(recipeName, recipeList, recipePrompt, event) {
        // event가 존재하지 않으면 return
        if (!event) {
            return;
        }
    
        // 체크박스를 클릭한 경우에는 모달을 열지 않음
        if (event.target.type === 'checkbox') {
            return;
        }
    
        // 모달 내용 설정
        document.getElementById('modal-recipe-name').textContent = recipeName;
        document.getElementById('modal-recipe-list').textContent = recipeList;
        document.getElementById('modal-recipe-prompt').textContent = `재료: ${recipePrompt}`; // 변수명 변경
    
        const imageElement = document.getElementById('modal-recipe-image');
        const imgElement = event.target.closest('.user-card').querySelector('img');
        
        if (imgElement && imgElement.src) {
            imageElement.src = imgElement.src;
            imageElement.style.display = 'block';
        } else {
            imageElement.style.display = 'none';
        }
    
        // 텍스트 포맷팅을 적용
        formatText(document.getElementById('modal-recipe-list'));
    
        // 모달과 배경 표시
        document.getElementById('recipe-modal').style.display = 'block';
        document.getElementById('recipe-modal-background').style.display = 'block';
    }    

    // 모달 닫기
    function closeModal() {
        document.getElementById('recipe-modal').style.display = 'none';
        document.getElementById('recipe-modal-background').style.display = 'none';
    }

    // 모달 배경 클릭 시 닫기
    document.getElementById('recipe-modal-background').addEventListener('click', closeModal);


    // 체크박스를 클릭할 때 이벤트 전파를 막음
    function checkboxClicked(event) {
        event.stopPropagation();
    }
