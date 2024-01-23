// CSRF 토큰을 가져오는 함수
function getCookie(name) {
    let cookieValue = null;
    console.log("Yet\n");
    if (document.cookie && document.cookie !== '') {
        console.log("if\n");
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    console.log(cookieValue);
    return cookieValue;
}

function deleteStudent(email) {
    var csrfToken = getCookie('csrftoken');
    // AJAX 요청 구현
    fetch('/grt/deletestudent/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload(); // 성공 시 페이지 새로고침
            } else {
                console.log(data.error);
                alert('삭제 실패');
            }
        })
        .catch(error => console.error('Error:', error));
}
