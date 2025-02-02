// Numeric input field
window.addEventListener('load', function() {
    let digit_inuputs = document.querySelectorAll('input[data-custom-type="numeric"]');

    digit_inuputs.forEach(function(input) {
        let digits = input.parentElement
            .querySelector('.input-field-numeric-digits')
            .querySelectorAll('input[data-custom-type="numeric-digit"]');

        document.addEventListener("paste", function (e) {
            if (!input.parentElement.contains(document.activeElement)) return;
            e.preventDefault();
            let data = (e.clipboardData || window.clipboardData).getData("text");
            if (data.length == digits.length && !isNaN(+data)) {
                for (let i = 0; i < digits.length; i++) {
                    digits[i].value = data[i];
                }
                digits[digits.length - 1].focus();
            }
        });

        digits.forEach(function(digit, index) {
            digit.addEventListener('keydown', function(e) {
                if (e.ctrlKey) return;
                e.preventDefault();

                function moveCarret(delta) {
                    let new_index = index + delta;
                    if (new_index < 0) {
                        new_index = digits.length - 1;
                    } else if (new_index >= digits.length) {
                        new_index = 0;
                    }
                    digits[new_index].focus();
                }

                if (e.key == "ArrowLeft") {
                    return moveCarret(-1);
                } else if (e.key == "ArrowRight") {
                    return moveCarret(1);
                } else if (e.key == "Backspace") {
                    for (let i = digits.length - 1; i >= 0; i--) {
                        if (digits[i].value != '') {
                            digits[i].value = '';
                            digits[Math.max(i-1, 0)].focus();
                            return;
                        }
                    }
                }

                let number = +e.key;
                if (isNaN(number)) return;

                digit.value = number;
                if (index < digits.length - 1) {
                    digits[index + 1].focus();
                } else {
                    digits[0].focus();
                }

                let full_number = '';
                for (let i = 0; i < digits.length; i++) {
                    full_number += digits[i].value;
                }
                input.value = full_number;
            });
        });
    });
});