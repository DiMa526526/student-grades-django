document.addEventListener('DOMContentLoaded', function() {
    // Элементы модального окна
    const modal = document.getElementById('gradeModal');
    const modalTitle = document.getElementById('modalTitle');
    const gradeInput = document.getElementById('gradeInput');
    const submitBtn = document.getElementById('submitBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const deleteBtn = document.getElementById('deleteBtn');
    const dateInputContainer = document.getElementById('dateInputContainer');
    const newDateInput = document.getElementById('newDateInput');

    // Текущие данные оценки
    let currentCell = null;
    let isEditMode = false;
    let isNewDateMode = false;

    // Обработчики кликов по ячейкам
    document.querySelectorAll('.grade-cell').forEach(cell => {
        cell.addEventListener('click', function() {
            currentCell = this;
            const gradeValue = this.textContent.trim();
            isEditMode = gradeValue !== '';
            isNewDateMode = this.classList.contains('empty') && !isEditMode;

            // Настройка модального окна
            modalTitle.textContent = isEditMode ? 'Изменить оценку' : 'Добавить оценку';
            gradeInput.value = isEditMode ? gradeValue : '';
            deleteBtn.style.display = isEditMode ? 'block' : 'none';

            // Показать поле для даты только для новых оценок
            dateInputContainer.style.display = isNewDateMode ? 'block' : 'none';
            if (isNewDateMode) {
                newDateInput.valueAsDate = new Date(); // Установить текущую дату по умолчанию
            }

            // Показать модальное окно
            modal.style.display = 'block';
            gradeInput.focus();
        });
    });

    // Обработчик сохранения оценки
    submitBtn.addEventListener('click', async function() {
        const value = gradeInput.value;
        if (value < 2 || value > 5) {
            alert('Оценка должна быть от 2 до 5');
            return;
        }

        try {
            const studentId = currentCell.dataset.studentId;
            let date;

            // Если это новая дата, берем из поля ввода
            if (isNewDateMode) {
                date = newDateInput.value;
                if (!date) {
                    alert('Пожалуйста, выберите дату');
                    return;
                }
            } else {
                date = currentCell.dataset.date;
            }

            const url = isEditMode ? '/update-grade/' : '/add-grade/';
            const data = {
                student_id: studentId,
                date: date,
                value: value,
                discipline_id: getUrlParameter('discipline'),
                group_id: getUrlParameter('group')
            };

            if (isEditMode) {
                data.grade_id = currentCell.dataset.gradeId;
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || 'Ошибка сервера');
            }

            if (result.status === 'success') {
                location.reload();
            } else {
                alert('Ошибка: ' + (result.message || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Произошла ошибка: ' + error.message);
        } finally {
            modal.style.display = 'none';
        }
    });

    // Обработчик удаления оценки
    deleteBtn.addEventListener('click', async function() {
        if (confirm('Вы уверены, что хотите удалить эту оценку?')) {
            try {
                const gradeId = currentCell.dataset.gradeId;

                const response = await fetch('/delete-grade/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        grade_id: gradeId
                    })
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.message || 'Ошибка сервера');
                }

                if (result.status === 'success') {
                    location.reload();
                } else {
                    alert('Ошибка: ' + (result.message || 'Неизвестная ошибка'));
                }
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка: ' + error.message);
            } finally {
                modal.style.display = 'none';
            }
        }
    });

    cancelBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Закрытие модального окна при клике вне его
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Функция для получения параметров URL
    function getUrlParameter(name) {
        name = name.replace(/[\[\]]/g, '\\$&');
        const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)');
        const results = regex.exec(window.location.href);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, ' '));
    }
});