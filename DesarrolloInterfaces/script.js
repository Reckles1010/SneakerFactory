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

/* CUSTOMIZER */


document.addEventListener("DOMContentLoaded", () => {
    const stage = document.getElementById("customizerStage");
    const shoePreview = document.getElementById("shoePreview");
    const sockPreview = document.getElementById("sockPreview");
    const stageCaption = document.getElementById("stageCaption");
    const priceValue = document.getElementById("priceValue");
    const colorPalette = document.getElementById("colorPalette");
    const selectedColorLabel = document.getElementById("selectedColorLabel");
    const designSummary = document.getElementById("designSummary");
    const feedback = document.getElementById("feedback");

    const colors = [
        { name: "Blanco", value: "#f4f4f5", className: "white" },
        { name: "Negro", value: "#080808", className: "black" },
        { name: "Turquesa", value: "#179fb5", className: "blue" },
        { name: "Azul marino", value: "#142e50", className: "navy" },
        { name: "Coral", value: "#f17a54", className: "orange" },
        { name: "Amarillo", value: "#f5c45e", className: "yellow" },
        { name: "Rosa", value: "#e7a5b5", className: "pink" },
        { name: "Verde", value: "#78977b", className: "green" }
    ];

    const initialState = {
        product: "shoe",
        design: "classic",
        zone: "main",
        pattern: "none",
        colors: {
            main: "#f4f4f5",
            panel: "#179fb5",
            sole: "#f4f4f5",
            laces: "#080808"
        },
        sockColors: {
            main: "#179fb5",
            panel: "#f4f4f5"
        }
    };

    let state = cloneState(initialState);

    function cloneState(value) {
        return JSON.parse(JSON.stringify(value));
    }

    function getActiveColors() {
        return state.product === "sock"
            ? state.sockColors
            : state.colors;
    }

    function getAvailableZones() {
        if (state.product === "sock") {
            return [
                { key: "main", label: "Base" },
                { key: "panel", label: "Puño" }
            ];
        }

        return [
            { key: "main", label: "Base" },
            { key: "panel", label: "Panel" },
            { key: "sole", label: "Suela" },
            { key: "laces", label: "Cordones" }
        ];
    }

    function renderProduct() {
        /* Cada producto se muestra de forma independiente */
        shoePreview.hidden = state.product === "sock";
        sockPreview.hidden = state.product === "shoe";

        stage.classList.toggle(
            "customizer__stage--set",
            state.product === "set"
        );

        stageCaption.hidden = state.product === "set";

        stageCaption.textContent =
            state.product === "sock"
                ? "CALCETINES MERCURY"
                : "ZAPATILLAS MERCURY";

        document.querySelectorAll("[data-product]").forEach(button => {
            const selected = button.dataset.product === state.product;

            button.classList.toggle(
                "customizer__product--selected",
                selected
            );

            button.setAttribute("aria-pressed", String(selected));
        });

        document.querySelectorAll("[data-zone]").forEach(button => {
            const available = getAvailableZones().some(
                zone => zone.key === button.dataset.zone
            );

            button.hidden = !available;

            button.classList.toggle(
                "customizer__zone--selected",
                button.dataset.zone === state.zone
            );
        });

        renderPalette();
        renderColors();
        renderPrice();
        renderSummary();
    }

    function renderPalette() {
        const activeColors = getActiveColors();
        const currentColor = activeColors[state.zone] || "#f4f4f5";

        colorPalette.innerHTML = "";

        colors.forEach(color => {
            const button = document.createElement("button");

            button.type = "button";
            button.className =
                `customizer__swatch customizer__swatch--${color.className}`;

            button.title = color.name;
            button.setAttribute("aria-label", color.name);
            button.setAttribute(
                "aria-pressed",
                String(color.value === currentColor)
            );

            if (color.value === currentColor) {
                button.classList.add("customizer__swatch--selected");
            }

            button.addEventListener("click", () => {
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

    function renderColors() {
        /* Colores de las zapatillas */
        Object.entries(state.colors).forEach(([zone, value]) => {
            const properties = {
                main: "--shoe-main-color",
                panel: "--shoe-panel-color",
                sole: "--shoe-sole-color",
                laces: "--shoe-laces-color"
            };

            const property = properties[zone];

            if (property) {
                stage.style.setProperty(property, value);
            }
        });

        /* Colores de los calcetines */
        Object.entries(state.sockColors).forEach(([zone, value]) => {
            const properties = {
                main: "--sock-main-color",
                panel: "--sock-panel-color"
            };

            const property = properties[zone];

            if (property) {
                stage.style.setProperty(property, value);
            }
        });

        const shoePattern = document.getElementById("shoePattern");
        const sockPattern = document.getElementById("sockPattern");

        const patternMarkup = {
            none: "",
            dots: '<circle cx="6" cy="6" r="3" fill="#ffffff" opacity=".7"/>',
            stripes: '<path d="M-6 24 L24 -6 M6 30 L30 6" stroke="#ffffff" stroke-width="5" opacity=".65"/>',
            graphic: '<path d="M0 0 L12 0 L24 24 L12 24Z" fill="#ffffff" opacity=".35"/><circle cx="6" cy="6" r="3" fill="#080808" opacity=".35"/>'
        };

        const markup = patternMarkup[state.pattern] || "";

        shoePattern.innerHTML = markup;
        sockPattern.innerHTML = markup;

        stage.dataset.pattern = state.pattern;
    }

    function renderPrice() {
        let price;

        if (state.product === "sock") {
            price = 12.99;
        } else if (state.product === "set") {
            price = 99.99;
        } else {
            price = 89.99;
        }

        if (state.pattern !== "none") {
            price += 5;
        }

        priceValue.textContent =
            `${price.toFixed(2).replace(".", ",")} €`;
    }

    function renderSummary() {
        const productNames = {
            shoe: "Zapatillas",
            sock: "Calcetines",
            set: "Conjunto de zapatillas y calcetines"
        };

        const designNames = {
            classic: "Essential",
            ocean: "Ocean",
            sunset: "Sunset",
            graphic: "Graphic"
        };

        const activeColors = getActiveColors();

        const color = colors.find(
            item => item.value === activeColors.main
        );

        const patternNames = {
            none: "sin estampado",
            dots: "con puntos",
            stripes: "con rayas",
            graphic: "con estampado gráfico"
        };

        designSummary.textContent =
            `${productNames[state.product]} ${designNames[state.design]}, ` +
            `base ${color ? color.name.toLowerCase() : activeColors.main}, ` +
            `${patternNames[state.pattern]}. ` +
            `Precio estimado: ${priceValue.textContent}`;
    }

    function setDesign(design) {
        state.design = design;

        const presets = {
            classic: {
                main: "#f4f4f5",
                panel: "#179fb5",
                sole: "#f4f4f5",
                laces: "#080808"
            },
            ocean: {
                main: "#142e50",
                panel: "#179fb5",
                sole: "#f4f4f5",
                laces: "#f4f4f5"
            },
            sunset: {
                main: "#f17a54",
                panel: "#f5c45e",
                sole: "#080808",
                laces: "#080808"
            },
            graphic: {
                main: "#f4f4f5",
                panel: "#080808",
                sole: "#179fb5",
                laces: "#179fb5"
            }
        };

        state.colors = { ...presets[design] };

        state.sockColors = {
            main: presets[design].main,
            panel: presets[design].panel
        };

        document.querySelectorAll("[data-design]").forEach(button => {
            button.classList.toggle(
                "customizer__design--selected",
                button.dataset.design === design
            );
        });

        renderPalette();
        renderColors();
        renderPrice();
        renderSummary();
    }

    /* Cambiar entre zapatillas, calcetines y conjunto */
    document.querySelectorAll("[data-product]").forEach(button => {
        button.addEventListener("click", () => {
            state.product = button.dataset.product;

            const zones = getAvailableZones();

            if (!zones.some(zone => zone.key === state.zone)) {
                state.zone = "main";
            }

            renderProduct();
        });
    });

    /* Elegir una zona */
    document.querySelectorAll("[data-zone]").forEach(button => {
        button.addEventListener("click", () => {
            state.zone = button.dataset.zone;

            document.querySelectorAll("[data-zone]").forEach(zoneButton => {
                zoneButton.classList.toggle(
                    "customizer__zone--selected",
                    zoneButton.dataset.zone === state.zone
                );
            });

            renderPalette();
        });
    });

    /* Elegir un diseño */
    document.querySelectorAll("[data-design]").forEach(button => {
        button.addEventListener("click", () => {
            setDesign(button.dataset.design);
        });
    });

    /* Elegir un estampado */
    document.querySelectorAll(".customizer__pattern[data-pattern]").forEach(button => {
        button.addEventListener("click", () => {
            state.pattern = button.dataset.pattern;

            document.querySelectorAll(".customizer__pattern[data-pattern]").forEach(patternButton => {
                patternButton.classList.toggle(
                    "customizer__pattern--selected",
                    patternButton.dataset.pattern === state.pattern
                );
            });

            renderColors();
            renderPrice();
            renderSummary();
        });
    });

    /* Restablecer */
    document.getElementById("resetButton").addEventListener("click", () => {
        state = cloneState(initialState);

        document.querySelectorAll("[data-design]").forEach(button => {
            button.classList.toggle(
                "customizer__design--selected",
                button.dataset.design === state.design
            );
        });

        document.querySelectorAll(".customizer__pattern[data-pattern]").forEach(button => {
            button.classList.toggle(
                "customizer__pattern--selected",
                button.dataset.pattern === state.pattern
            );
        });

        renderProduct();
        feedback.textContent = "Diseño restablecido.";
    });

    document.getElementById("saveButton").addEventListener("click", () => {
        feedback.textContent =
            "Diseño preparado. Esta demo no guarda datos en una cuenta.";
    });

    document.getElementById("copyButton").addEventListener("click", async () => {
        const text = designSummary.textContent;

        try {
            await navigator.clipboard.writeText(text);
            feedback.textContent = "Resumen copiado al portapapeles.";
        } catch {
            feedback.textContent = text;
        }
    });

    renderProduct();
});
