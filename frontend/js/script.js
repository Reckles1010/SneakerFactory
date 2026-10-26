
/* CART */

document.addEventListener('DOMContentLoaded', () => {
    let cartCount = localStorage.getItem('cartCount')
        ? parseInt(localStorage.getItem('cartCount'))
        : 0;

    const cartBadge = document.getElementById('cartCount');

    if (cartBadge) {
        cartBadge.textContent = cartCount;
    }

    /* FILTROS DE PRODUCTOS */

    const filterBtns = document.querySelectorAll('.catalog__filter-btn');
    const productCards = document.querySelectorAll('.catalog__grid .card, #productGrid .card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => {
                b.classList.remove('catalog__filter-btn--active');
            });

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

    /* FAVORITOS */

    const favoriteBtns = document.querySelectorAll('.card__favorite-btn');

    favoriteBtns.forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            btn.classList.toggle('card__favorite-btn--active');
        });
    });

    /* AÑADIR AL CARRITO */

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

    /* NEWSLETTER */

    const newsletterForm = document.getElementById('newsletterForm');
    const newsletterFeedback = document.getElementById('newsletterFeedback');

    if (newsletterForm) {
        newsletterForm.addEventListener('submit', e => {
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

    /* VALIDACIÓN DEL CORREO ELECTRÓNICO */

    const isValidEmail = email => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    };

    /* INICIAR SESIÓN */

    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        const emailInput = document.getElementById('loginEmail');
        const passwordInput = document.getElementById('loginPassword');
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');

        loginForm.addEventListener('submit', e => {
            e.preventDefault();

            let valid = true;

            if (!isValidEmail(emailInput.value.trim())) {
                emailInput.classList.add('auth__form-input--error');
                emailError.classList.add('auth__form-error--active');
                valid = false;
            } else {
                emailInput.classList.remove('auth__form-input--error');
                emailError.classList.remove('auth__form-error--active');
            }

            if (passwordInput.value.trim().length < 6) {
                passwordInput.classList.add('auth__form-input--error');
                passwordError.classList.add('auth__form-error--active');
                valid = false;
            } else {
                passwordInput.classList.remove('auth__form-input--error');
                passwordError.classList.remove('auth__form-error--active');
            }

            if (valid) {
                const submitBtn = loginForm.querySelector('.auth__form-submit-btn span');

                if (submitBtn) {
                    submitBtn.textContent = 'Accediendo...';
                }

                setTimeout(() => {
                    window.location.href = 'inicio.html';
                }, 1000);
            }
        });
    }

    /* REGISTRO */

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

        registerForm.addEventListener('submit', e => {
            e.preventDefault();

            let valid = true;

            if (nameInput.value.trim() === '') {
                nameInput.classList.add('auth__form-input--error');
                nameError.classList.add('auth__form-error--active');
                valid = false;
            } else {
                nameInput.classList.remove('auth__form-input--error');
                nameError.classList.remove('auth__form-error--active');
            }

            if (lastNameInput.value.trim() === '') {
                lastNameInput.classList.add('auth__form-input--error');
                lastNameError.classList.add('auth__form-error--active');
                valid = false;
            } else {
                lastNameInput.classList.remove('auth__form-input--error');
                lastNameError.classList.remove('auth__form-error--active');
            }

            if (!isValidEmail(emailInput.value.trim())) {
                emailInput.classList.add('auth__form-input--error');
                regEmailError.classList.add('auth__form-error--active');
                valid = false;
            } else {
                emailInput.classList.remove('auth__form-input--error');
                regEmailError.classList.remove('auth__form-error--active');
            }

            if (passwordInput.value.trim().length < 8) {
                passwordInput.classList.add('auth__form-input--error');
                regPasswordError.classList.add('auth__form-error--active');
                valid = false;
            } else {
                passwordInput.classList.remove('auth__form-input--error');
                regPasswordError.classList.remove('auth__form-error--active');
            }

            if (!termsCheck.checked) {
                termsError.classList.add('auth__form-error--active');
                valid = false;
            } else {
                termsError.classList.remove('auth__form-error--active');
            }

            if (valid) {
                const submitBtn = registerForm.querySelector('.auth__form-submit-btn span');

                if (submitBtn) {
                    submitBtn.textContent = 'Creando cuenta...';
                }

                setTimeout(() => {
                    window.location.href = 'inicio.html';
                }, 1000);
            }
        });
    }
});


/* CUSTOMIZER */

document.addEventListener('DOMContentLoaded', () => {
    const stage = document.getElementById('customizerStage');
    const shoePreview = document.getElementById('shoePreview');
    const sockPreview = document.getElementById('sockPreview');
    const stageCaption = document.getElementById('stageCaption');
    const priceValue = document.getElementById('priceValue');
    const colorPalette = document.getElementById('colorPalette');
    const selectedColorLabel = document.getElementById('selectedColorLabel');
    const designSummary = document.getElementById('designSummary');
    const feedback = document.getElementById('feedback');

    /* COLORES DISPONIBLES */

    const colors = [
        { name: 'Blanco', value: '#f4f4f5', className: 'white' },
        { name: 'Negro', value: '#080808', className: 'black' },
        { name: 'Turquesa', value: '#179fb5', className: 'blue' },
        { name: 'Azul marino', value: '#142e50', className: 'navy' },
        { name: 'Morado', value: '#8c04a0', className: 'purple' },
        { name: 'Violeta', value: '#7e04f0', className: 'violet' },
        { name: 'Rosa', value: '#e7a5b5', className: 'pink' },
        { name: 'Verde', value: '#78977b', className: 'green' }
    ];

    /* ESTADO INICIAL */

    const initialState = {
        product: 'shoe',
        design: 'classic',
        zone: 'main',

        colors: {
            main: '#f4f4f5',
            panel: '#179fb5',
            sole: '#f4f4f5',
            laces: '#080808'
        },

        sockColors: {
            main: '#179fb5',
            panel: '#f4f4f5'
        }
    };

    let state = cloneState(initialState);

    function cloneState(value) {
        return JSON.parse(JSON.stringify(value));
    }

    /* OBTENER COLORES DEL PRODUCTO ACTUAL */

    function getActiveColors() {
        return state.product === 'sock'
            ? state.sockColors
            : state.colors;
    }

    /* ZONAS DISPONIBLES */

    function getAvailableZones() {
        if (state.product === 'sock') {
            return [
                { key: 'main', label: 'Base' },
                { key: 'panel', label: 'Puño' }
            ];
        }

        return [
            { key: 'main', label: 'Base' },
            { key: 'panel', label: 'Panel' },
            { key: 'sole', label: 'Suela' },
            { key: 'laces', label: 'Cordones' }
        ];
    }

    /* MOSTRAR EL PRODUCTO */

    function renderProduct() {
        shoePreview.hidden = state.product === 'sock';
        sockPreview.hidden = state.product === 'shoe';

        stage.classList.toggle(
            'customizer__stage--set',
            state.product === 'set'
        );

        stageCaption.hidden = state.product === 'set';

        stageCaption.textContent =
            state.product === 'sock'
                ? 'CALCETINES MERCURY'
                : 'ZAPATILLAS MERCURY';

        document.querySelectorAll('[data-product]').forEach(button => {
            const selected = button.dataset.product === state.product;

            button.classList.toggle(
                'customizer__product--selected',
                selected
            );

            button.setAttribute('aria-pressed', String(selected));
        });

        document.querySelectorAll('[data-zone]').forEach(button => {
            const available = getAvailableZones().some(
                zone => zone.key === button.dataset.zone
            );

            button.hidden = !available;

            button.classList.toggle(
                'customizer__zone--selected',
                button.dataset.zone === state.zone
            );
        });

        renderPalette();
        renderColors();
        renderPrice();
        renderSummary();
    }

    /* PALETA DE COLORES */

    function renderPalette() {
        const activeColors = getActiveColors();
        const currentColor = activeColors[state.zone] || '#f4f4f5';

        colorPalette.innerHTML = '';

        colors.forEach(color => {
            const button = document.createElement('button');

            button.type = 'button';

            button.className =
                `customizer__swatch customizer__swatch--${color.className}`;

            button.title = color.name;
            button.setAttribute('aria-label', color.name);

            button.setAttribute(
                'aria-pressed',
                String(color.value === currentColor)
            );

            if (color.value === currentColor) {
                button.classList.add('customizer__swatch--selected');
            }

            button.addEventListener('click', () => {
                getActiveColors()[state.zone] = color.value;

                renderPalette();
                renderColors();
                renderSummary();
            });

            colorPalette.appendChild(button);
        });

        const found = colors.find(
            color => color.value === currentColor
        );

        selectedColorLabel.textContent =
            `Color seleccionado: ${found ? found.name : currentColor}`;
    }

    /* APLICAR COLORES */

    function renderColors() {
        /* Colores de las zapatillas */

        Object.entries(state.colors).forEach(([zone, value]) => {
            const properties = {
                main: '--shoe-main-color',
                panel: '--shoe-panel-color',
                sole: '--shoe-sole-color',
                laces: '--shoe-laces-color'
            };

            const property = properties[zone];

            if (property) {
                stage.style.setProperty(property, value);
            }
        });

        /* Colores de los calcetines */

        Object.entries(state.sockColors).forEach(([zone, value]) => {
            const properties = {
                main: '--sock-main-color',
                panel: '--sock-panel-color'
            };

            const property = properties[zone];

            if (property) {
                stage.style.setProperty(property, value);
            }
        });
    }

    /* CALCULAR PRECIO */

    function renderPrice() {
        let price;

        if (state.product === 'sock') {
            price = 12.99;
        } else if (state.product === 'set') {
            price = 99.99;
        } else {
            price = 89.99;
        }

        priceValue.textContent =
            `${price.toFixed(2).replace('.', ',')} €`;
    }

    /* RESUMEN DEL DISEÑO */

    function renderSummary() {
        const productNames = {
            shoe: 'Zapatillas',
            sock: 'Calcetines',
            set: 'Conjunto de zapatillas y calcetines'
        };

        const designNames = {
            classic: 'Essential',
            ocean: 'Ocean',
            lavander: 'Lavander',
            graphic: 'Graphic'
        };

        const activeColors = getActiveColors();

        const color = colors.find(
            item => item.value === activeColors.main
        );

        designSummary.textContent =
            `${productNames[state.product]} ${designNames[state.design]}, ` +
            `base ${color ? color.name.toLowerCase() : activeColors.main}. ` +
            `Precio estimado: ${priceValue.textContent}`;
    }

    /* CAMBIAR DISEÑO */

    function setDesign(design) {
        state.design = design;

        const presets = {
            classic: {
                main: '#f4f4f5',
                panel: '#179fb5',
                sole: '#f4f4f5',
                laces: '#080808'
            },

            ocean: {
                main: '#142e50',
                panel: '#179fb5',
                sole: '#f4f4f5',
                laces: '#f4f4f5'
            },

            lavander: {
                main: ' #f4f4f5',
                panel: '#8c04a0',
                sole: '#7e04f0',
                laces: '#f4f4f5'
            },

            graphic: {
                main: '#f4f4f5',
                panel: '#080808',
                sole: '#179fb5',
                laces: '#179fb5'
            }
        };

        state.colors = { ...presets[design] };

        state.sockColors = {
            main: presets[design].main,
            panel: presets[design].panel
        };

        document.querySelectorAll('[data-design]').forEach(button => {
            button.classList.toggle(
                'customizer__design--selected',
                button.dataset.design === design
            );
        });

        renderPalette();
        renderColors();
        renderPrice();
        renderSummary();
    }

    /* CAMBIAR ENTRE PRODUCTOS */

    document.querySelectorAll('[data-product]').forEach(button => {
        button.addEventListener('click', () => {
            state.product = button.dataset.product;

            const zones = getAvailableZones();

            if (!zones.some(zone => zone.key === state.zone)) {
                state.zone = 'main';
            }

            renderProduct();
        });
    });

    /* SELECCIONAR ZONA */

    document.querySelectorAll('[data-zone]').forEach(button => {
        button.addEventListener('click', () => {
            state.zone = button.dataset.zone;

            document.querySelectorAll('[data-zone]').forEach(zoneButton => {
                zoneButton.classList.toggle(
                    'customizer__zone--selected',
                    zoneButton.dataset.zone === state.zone
                );
            });

            renderPalette();
        });
    });

    /* SELECCIONAR DISEÑO */

    document.querySelectorAll('[data-design]').forEach(button => {
        button.addEventListener('click', () => {
            setDesign(button.dataset.design);
        });
    });

    /* RESTABLECER PERSONALIZACIÓN */

    const resetButton = document.getElementById('resetButton');

    if (resetButton) {
        resetButton.addEventListener('click', () => {
            state = cloneState(initialState);

            document.querySelectorAll('[data-design]').forEach(button => {
                button.classList.toggle(
                    'customizer__design--selected',
                    button.dataset.design === state.design
                );
            });

            renderProduct();

            feedback.textContent = 'Diseño restablecido.';
        });
    }

    /* GUARDAR DISEÑO */

    const saveButton = document.getElementById('saveButton');

    if (saveButton) {
        saveButton.addEventListener('click', () => {
            feedback.textContent =
                'Diseño preparado. Esta demo no guarda datos en una cuenta.';
        });
    }

    /* INICIALIZAR PERSONALIZADOR */

    if (
        stage &&
        shoePreview &&
        sockPreview &&
        stageCaption &&
        priceValue &&
        colorPalette &&
        selectedColorLabel &&
        designSummary &&
        feedback
    ) {
        renderProduct();
    }
});
