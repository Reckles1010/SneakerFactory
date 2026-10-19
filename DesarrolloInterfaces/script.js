document.addEventListener('DOMContentLoaded', () => {
    let cartCount = localStorage.getItem('cartCount') ? parseInt(localStorage.getItem('cartCount')) : 0;
    const cartBadge = document.getElementById('cartCount');
    if (cartBadge) {
        cartBadge.textContent = cartCount;
    }

    const filterBtns = document.querySelectorAll('.catalog__filter-btn');
    const productCards = document.querySelectorAll('.catalog__grid .card, #productGrid .card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('catalog__filter-btn--active'));
            btn.classList.add('catalog__filter-btn--active');

            const filterValue = btn.getAttribute('data-filter');

            productCards.forEach(card => {
                const category = card.getAttribute('data-category');
                if (filterValue === 'all' || category === filterValue) {
                    card.style.display = 'flex';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'scale(1)';
                    }, 50);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 200);
                }
            });
        });
    });

    const favoriteBtns = document.querySelectorAll('.card__favorite-btn');
    favoriteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            btn.classList.toggle('card__favorite-btn--active');
        });
    });

    const addToCartBtns = document.querySelectorAll('.card__overlay-btn');

    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            cartCount++;
            localStorage.setItem('cartCount', cartCount);
            if (cartBadge) {
                cartBadge.textContent = cartCount;
            }
            
            const spanText = btn.querySelector('span');
            if (spanText) {
                const originalText = spanText.textContent;
                spanText.textContent = '¡Añadido!';
                btn.style.backgroundColor = 'var(--color-accent-neon)';
                btn.style.color = 'var(--color-black)';

                setTimeout(() => {
                    spanText.textContent = originalText;
                    btn.style.backgroundColor = 'var(--color-black)';
                    btn.style.color = 'var(--color-white)';
                }, 1200);
            }
        });
    });

    const newsletterForm = document.getElementById('newsletterForm');
    const newsletterFeedback = document.getElementById('newsletterFeedback');

    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (newsletterFeedback) {
                newsletterFeedback.classList.add('newsletter__feedback--success');
            }
            newsletterForm.reset();

            setTimeout(() => {
                if (newsletterFeedback) {
                    newsletterFeedback.classList.remove('newsletter__feedback--success');
                }
            }, 4000);
        });
    }

    const isValidEmail = (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    };

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        const emailInput = document.getElementById('loginEmail');
        const passwordInput = document.getElementById('loginPassword');
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');

        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            let valid = true;

            if (!isValidEmail(emailInput.value.trim())) {
                emailInput.classList.add('auth-form__input--error');
                emailError.classList.add('auth-form__error--active');
                valid = false;
            } else {
                emailInput.classList.remove('auth-form__input--error');
                emailError.classList.remove('auth-form__error--active');
            }

            if (passwordInput.value.trim().length < 6) {
                passwordInput.classList.add('auth-form__input--error');
                passwordError.classList.add('auth-form__error--active');
                valid = false;
            } else {
                passwordInput.classList.remove('auth-form__input--error');
                passwordError.classList.remove('auth-form__error--active');
            }

            if (valid) {
                const submitBtn = loginForm.querySelector('.auth-form__submit-btn span');
                if (submitBtn) submitBtn.textContent = 'Accediendo...';
                
                setTimeout(() => {
                    window.location.href = 'inicio.html';
                }, 1000);
            }
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        const nameInput = document.getElementById('regName');
        const lastNameInput = document.getElementById('regLastName');
        const emailInput = document.getElementById('regEmail');
        const passwordInput = document.getElementById('regPassword');
        const termsCheck = document.getElementById('termsCheck');

        const nameError = document.getElementById('nameError');
        const lastNameError = document.getElementById('lastNameError');
        const regEmailError = document.getElementById('regEmailError');
        const regPasswordError = document.getElementById('regPasswordError');
        const termsError = document.getElementById('termsError');

        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            let valid = true;

            if (nameInput.value.trim() === '') {
                nameInput.classList.add('auth-form__input--error');
                nameError.classList.add('auth-form__error--active');
                valid = false;
            } else {
                nameInput.classList.remove('auth-form__input--error');
                nameError.classList.remove('auth-form__error--active');
            }

            if (lastNameInput.value.trim() === '') {
                lastNameInput.classList.add('auth-form__input--error');
                lastNameError.classList.add('auth-form__error--active');
                valid = false;
            } else {
                lastNameInput.classList.remove('auth-form__input--error');
                lastNameError.classList.remove('auth-form__error--active');
            }

            if (!isValidEmail(emailInput.value.trim())) {
                emailInput.classList.add('auth-form__input--error');
                regEmailError.classList.add('auth-form__error--active');
                valid = false;
            } else {
                emailInput.classList.remove('auth-form__input--error');
                regEmailError.classList.remove('auth-form__error--active');
            }

            if (passwordInput.value.trim().length < 8) {
                passwordInput.classList.add('auth-form__input--error');
                regPasswordError.classList.add('auth-form__error--active');
                valid = false;
            } else {
                passwordInput.classList.remove('auth-form__input--error');
                regPasswordError.classList.remove('auth-form__error--active');
            }

            if (!termsCheck.checked) {
                termsError.classList.add('auth-form__error--active');
                valid = false;
            } else {
                termsError.classList.remove('auth-form__error--active');
            }

            if (valid) {
                const submitBtn = registerForm.querySelector('.auth-form__submit-btn span');
                if (submitBtn) submitBtn.textContent = 'Creando cuenta...';

                setTimeout(() => {
                    window.location.href = 'inicio.html';
                }, 1000);
            }
        });
    }
});