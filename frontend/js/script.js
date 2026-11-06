
/* BASE DE DATOS*/

const API_URL = 'http://localhost:3000/api';

const CART_KEY = 'mercuryCart';
const USER_KEY = 'mercuryUser';

const SHIPPING_PRICE = 0;

const currency = new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR'
});


/* GESTIÓN CARRITO */

/* Recuperar productos */
function getCart() {
    try {
        return JSON.parse(localStorage.getItem(CART_KEY)) || [];
    } catch (error) {
        console.error('Error al recuperar el carrito:', error);
        return [];
    }
}

/* Guardar productos */
function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));

    updateCartBadge();

    document.dispatchEvent(new CustomEvent('cartUpdated'));
}

/* Número total de unidades */
function getCartCount() {
    return getCart().reduce((total, product) => {
        return total + (Number(product.quantity) || 1);
    }, 0);
}

/* Actualizar contador en todas las páginas */
function updateCartBadge() {
    const badges = document.querySelectorAll('#cartCount');

    badges.forEach(badge => {
        badge.textContent = getCartCount();
    });
}

/* Añadir producto */

document.querySelectorAll('.card__overlay-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const card = btn.closest('.card');

        if (!card) return;

        const name = card.querySelector('.card__title');
        const image = card.querySelector('.card__image');

        if (!name || !image) return;

        const category = card.dataset.category;

        const product = {
            id: btn.dataset.id || name.textContent.trim(),
            name: name.textContent.trim(),
            price: Number(btn.dataset.price) || 0,
            size: btn.dataset.size || (
                category === 'zapatillas' ? 'Sin especificar' : 'Única'
            ),
            image: image.src,
            customization: null
        };

        if (category === 'zapatillas' && product.size === 'Sin especificar') {
            alert('Selecciona una talla antes de continuar.');
            return;
        }

        addProductToCart(product);

        delete btn.dataset.size;

        const spanText = btn.querySelector('span');

        if (spanText) {
            const originalText = spanText.textContent;

            spanText.textContent = '¡Añadido!';

            setTimeout(() => {
                spanText.textContent = originalText;
            }, 1200);
        }
    });
});


/* Recuperar usuario */
function getCurrentUser() {
    try {
        return JSON.parse(localStorage.getItem(USER_KEY));
    } catch (error) {
        console.error('Error al recuperar el usuario:', error);
        return null;
    }
}


/* POPUP DEL CATÁLOGO */

document.addEventListener('DOMContentLoaded', () => {
    const productPopup = document.getElementById('productPopup');

    if (productPopup) {

        const popupClose = document.getElementById('popupClose');

        const popupImage = document.getElementById('popupImage');
        const popupTitle = document.getElementById('popupTitle');
        const popupPrice = document.getElementById('popupPrice');
        const popupCategory = document.getElementById('popupCategory');
        const popupBadge = document.getElementById('popupBadge');
        const popupDescription = document.getElementById('popupDescription');
        const popupColor = document.getElementById('popupColor');

        const popupAdd = document.getElementById('popupAdd');
        const popupAddPrice = document.getElementById('popupAddPrice');

        const productGrid = document.getElementById('productGrid');

        let selectedProduct = null;
        let selectedSize = null;

        if (productGrid) {

            productGrid.addEventListener('click', event => {
                if (event.target.closest('.card__overlay-btn--action')) {
                    return;
                }

                const card = event.target.closest('.card[data-category="zapatillas"]');

                if (!card) return;

                selectedProduct = card;

                const image = card.querySelector('.card__image');
                const name = card.querySelector('.card__title');
                const category = card.querySelector('.card__category');
                const badge = card.querySelector('.card__badge');

                const originalButton = card.querySelector(
                    '.card__overlay-btn--action'
                );

                if (!image || !name || !originalButton) return;

                const productPrice = Number(originalButton.dataset.price) || 0;

                popupImage.src = image.src;
                popupImage.alt = image.alt;

                popupTitle.textContent = name.textContent;
                popupCategory.textContent = category
                    ? category.textContent
                    : '';

                popupPrice.textContent = currency.format(productPrice);
                popupAddPrice.textContent = '— ' + currency.format(productPrice);

                if (badge) {
                    popupBadge.textContent = badge.textContent;
                    popupBadge.hidden = false;
                } else {
                    popupBadge.hidden = true;
                }

                popupDescription.textContent =
                    'Descubre ' + name.textContent +
                    ', una zapatilla diseñada para combinar comodidad, ' +
                    'estilo y personalidad en cada paso.';

                popupColor.textContent = 'Consultar variantes';

                selectedSize = null;

                document.querySelectorAll('.popup__size').forEach(size => {
                    size.classList.remove('popup__size--active');
                });

                productPopup.classList.add('popup--active');
                productPopup.setAttribute('aria-hidden', 'false');

                document.body.classList.add('product-popup-open');
            });
        }

        document.querySelectorAll('.popup__size').forEach(button => {
            button.addEventListener('click', function () {
                document.querySelectorAll('.popup__size').forEach(size => {
                    size.classList.remove('popup__size--active');
                });

                this.classList.add('popup__size--active');

                selectedSize = this.dataset.size;
            });
        });

        function closeProductPopup() {
            productPopup.classList.remove('popup--active');

            productPopup.setAttribute('aria-hidden', 'true');

            document.body.classList.remove('popup__open');

            selectedProduct = null;
            selectedSize = null;
        }

        if (popupClose) {
            popupClose.addEventListener('click', closeProductPopup);
        }

        productPopup.addEventListener('click', event => {
            if (event.target === productPopup) {
                closeProductPopup();
            }
        });

        document.addEventListener('keydown', event => {

            if (
                event.key === 'Escape' &&
                productPopup.classList.contains('popup--active')
            ) {
                closeProductPopup();
            }
        });

        if (popupAdd) {
            popupAdd.addEventListener('click', () => {

                if (!selectedProduct) return;

                if (!selectedSize) {
                    alert('Selecciona una talla antes de continuar.');
                    return;
                }

                const originalButton = selectedProduct.querySelector(
                    '.card__overlay-btn--action'
                );

                if (!originalButton) return;

                originalButton.dataset.size = selectedSize;

                originalButton.click();

                closeProductPopup();
            });
        }
    }


    /* FILTROS DEL CATÁLOGO */

    const filterBtns = document.querySelectorAll('.catalog__filter-btn');

    const productCards = document.querySelectorAll(
        '.catalog__grid .card, #productGrid .card'
    );

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(button => {
                button.classList.remove('catalog__filter-btn--active');
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

    document.querySelectorAll('.card__favorite-btn').forEach(btn => {
        btn.addEventListener('click', event => {
            event.stopPropagation();

            btn.classList.toggle('card__favorite-btn--active');
        });
    });


    /* AÑADIR PRODUCTOS DEL CATÁLOGO */

    document.querySelectorAll('.card__overlay-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const card = btn.closest('.card');

            if (!card) return;

            const name = card.querySelector('.card__title');
            const image = card.querySelector('.card__image');

            if (!name || !image) return;

            const price = Number(btn.dataset.price) || 0;

            const product = {
                id: btn.dataset.id || name.textContent.trim(),
                name: name.textContent.trim(),
                price: price,
                size: btn.dataset.size || 'Sin especificar',
                image: image.src,
                customization: null
            };

            addProductToCart(product);

            delete btn.dataset.size;

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

    updateCartBadge();

});


/* LOGIN Y REGISTRO */

document.addEventListener('DOMContentLoaded', () => {
    const isValidEmail = email => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    };

    const showError = (input, error) => {
        if (input) input.classList.add('auth__form-input--error');
        if (error) error.classList.add('auth__form-error--active');
    };

    const clearError = (input, error) => {
        if (input) input.classList.remove('auth__form-input--error');
        if (error) error.classList.remove('auth__form-error--active');
    };


    /* Iniciar sesión */

    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        const emailInput = document.getElementById('loginEmail');
        const passwordInput = document.getElementById('loginPassword');

        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');

        loginForm.addEventListener('submit', async event => {
            event.preventDefault();

            let valid = true;

            if (!isValidEmail(emailInput.value.trim())) {
                showError(emailInput, emailError);
                valid = false;
            } else {
                clearError(emailInput, emailError);
            }

            if (passwordInput.value.length < 8) {
                showError(passwordInput, passwordError);
                valid = false;
            } else {
                clearError(passwordInput, passwordError);
            }

            if (!valid) return;

            const submitBtn = loginForm.querySelector('.auth__form-submit-btn');
            const submitText = submitBtn.querySelector('span');

            submitBtn.disabled = true;

            if (submitText) submitText.textContent = 'Accediendo...';

            try {
                const response = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        email: emailInput.value.trim(),
                        password: passwordInput.value
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.message || 'Correo o contraseña incorrectos.'
                    );
                }

                if (data.user) {
                    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
                }

                window.location.href = 'inicio.html';

            } catch (error) {
                passwordError.textContent = error.message;
                passwordError.classList.add('auth__form-error--active');
            } finally {

                submitBtn.disabled = false;

                if (submitText) submitText.textContent = 'Iniciar sesión';
            }
        });
    }


    /* Registro */

    const registerForm = document.getElementById('registerForm');

    if (registerForm) {
        const nameInput = document.getElementById('regName');
        const lastNameInput = document.getElementById('regLastName');
        const emailInput = document.getElementById('regEmail');
        const passwordInput = document.getElementById('regPassword');

        const termsCheck = document.getElementById('termsCheck');

        const nameError = document.getElementById('nameError');
        const lastNameError = document.getElementById('lastNameError');
        const emailError = document.getElementById('regEmailError');
        const passwordError = document.getElementById('regPasswordError');
        const termsError = document.getElementById('termsError');

        registerForm.addEventListener('submit', async event => {
            event.preventDefault();

            let valid = true;

            if (nameInput.value.trim() === '') {
                showError(nameInput, nameError);
                valid = false;
            } else {
                clearError(nameInput, nameError);
            }

            if (lastNameInput.value.trim() === '') {
                showError(lastNameInput, lastNameError);
                valid = false;
            } else {
                clearError(lastNameInput, lastNameError);
            }

            if (!isValidEmail(emailInput.value.trim())) {
                showError(emailInput, emailError);
                valid = false;
            } else {
                clearError(emailInput, emailError);
            }

            if (passwordInput.value.length < 8) {
                showError(passwordInput, passwordError);
                valid = false;
            } else {
                clearError(passwordInput, passwordError);
            }

            if (!termsCheck.checked) {
                termsError.classList.add('auth__form-error--active');
                valid = false;
            } else {
                termsError.classList.remove('auth__form-error--active');
            }

            if (!valid) return;

            const submitBtn = registerForm.querySelector('.auth__form-submit-btn');
            const submitText = submitBtn.querySelector('span');

            submitBtn.disabled = true;

            if (submitText) submitText.textContent = 'Creando cuenta...';

            try {
                const response = await fetch(`${API_URL}/auth/register`, {
                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json'
                    },

                    body: JSON.stringify({
                        nombre: nameInput.value.trim(),
                        apellidos: lastNameInput.value.trim(),
                        email: emailInput.value.trim(),
                        password: passwordInput.value
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.message || 'No se ha podido crear la cuenta.'
                    );
                }

                window.location.href = 'login.html';
            } catch (error) {
                emailError.textContent = error.message;
                emailError.classList.add('auth__form-error--active');
            } finally {
                submitBtn.disabled = false;

                if (submitText) submitText.textContent = 'Crear cuenta';
            }
        });
    }


    /* GESTIÓN DE USUARIOS */

    const usersTableBody = document.getElementById('usersTableBody');

    if (usersTableBody) {
        const userSearch = document.getElementById('userSearch');
        const userCount = document.getElementById('userCount');
        const usersFeedback = document.getElementById('usersFeedback');

        const roles = [
            'cliente',
            'administrador',
            'almacen',
            'comercial',
            'encargado'
        ];

        let users = [];

        const showFeedback = (message, type) => {
            usersFeedback.textContent = message;
            usersFeedback.className = `users__feedback users__feedback--${type}`;
        };

        const renderUsers = (search = '') => {
            const filteredUsers = users.filter(user => {
                const fullName =
                    `${user.nombre} ${user.apellidos}`.toLowerCase();

                const email = user.email.toLowerCase();

                const value = search.toLowerCase();

                return fullName.includes(value) || email.includes(value);
            });

            userCount.textContent = `${filteredUsers.length} usuarios`;

            usersTableBody.innerHTML = '';

            if (filteredUsers.length === 0) {
                usersTableBody.innerHTML = `
                    <tr>
                        <td colspan="4" class="users__empty">
                            No se han encontrado usuarios.
                        </td>
                    </tr>
                `;

                return;
            }

            filteredUsers.forEach(user => {
                const row = document.createElement('tr');

                const nameCell = document.createElement('td');
                nameCell.textContent =
                    `${user.nombre} ${user.apellidos}`;

                const emailCell = document.createElement('td');
                emailCell.textContent = user.email;

                const roleCell = document.createElement('td');
                roleCell.textContent = user.rol;

                const selectCell = document.createElement('td');

                const roleSelect = document.createElement('select');

                roleSelect.dataset.userId = user.id;

                roleSelect.setAttribute(
                    'aria-label',
                    `Rol de ${user.nombre}`
                );

                roles.forEach(role => {
                    const option = document.createElement('option');

                    option.value = role;

                    option.textContent =
                        role.charAt(0).toUpperCase() + role.slice(1);

                    option.selected = user.rol === role;

                    roleSelect.appendChild(option);
                });

                roleSelect.addEventListener('change', () => {
                    updateUserRole(
                        user.id,
                        roleSelect.value,
                        roleCell,
                        roleSelect
                    );
                });

                selectCell.appendChild(roleSelect);

                row.append(
                    nameCell,
                    emailCell,
                    roleCell,
                    selectCell
                );
                usersTableBody.appendChild(row);
            });
        };

        const loadUsers = async () => {

            try {
                const response = await fetch(`${API_URL}/users`, {
                    credentials: 'include'
                });

                if (!response.ok) {
                    throw new Error(
                        'No tienes permiso para consultar los usuarios.'
                    );
                }

                users = await response.json();

                renderUsers();

            } catch (error) {
                usersTableBody.innerHTML = `
                    <tr>
                        <td colspan="4" class="users__empty">
                            ${error.message}
                        </td>
                    </tr>
                `;
            }
        };

        const updateUserRole = async (
            userId,
            newRole,
            roleCell,
            roleSelect
        ) => {

            roleSelect.disabled = true;

            try {
                const response = await fetch(
                    `${API_URL}/users/${userId}/role`,
                    {
                        method: 'PATCH',

                        headers: {
                            'Content-Type': 'application/json'
                        },

                        credentials: 'include',

                        body: JSON.stringify({
                            rol: newRole
                        })
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.message || 'No se ha podido modificar el rol.'
                    );
                }

                const user = users.find(
                    item => String(item.id) === String(userId)
                );

                if (user) user.rol = newRole;

                roleCell.textContent = newRole;

                showFeedback(
                    'El rol del usuario se ha actualizado correctamente.',
                    'success'
                );

            } catch (error) {
                showFeedback(error.message, 'error');

                await loadUsers();

            } finally {
                roleSelect.disabled = false;
            }
        };

        if (userSearch) {
            userSearch.addEventListener('input', () => {
                renderUsers(userSearch.value);
            });
        }
        loadUsers();
    }

});


/* PÁGINA DEL CARRITO */

document.addEventListener('DOMContentLoaded', () => {
    const cartItems = document.getElementById('cartItems');

    if (!cartItems) return;

    const loginRequired = document.getElementById('cartLoginRequired');
    const checkout = document.getElementById('cartCheckout');

    const cartEmpty = document.getElementById('cartEmpty');

    const cartCount = document.getElementById('cartCount');
    const productCount = document.getElementById('cartProductCount');

    const subtotalElement = document.getElementById('summarySubtotal');
    const shippingElement = document.getElementById('summaryShipping');
    const totalElement = document.getElementById('summaryTotal');

    const checkoutForm = document.getElementById('checkoutForm');
    const feedback = document.getElementById('cartFeedback');

    const confirmButton = document.getElementById('confirmOrder');

    function checkSession() {
        const user = getCurrentUser();

        if (user) {
            if (loginRequired) loginRequired.hidden = true;
            if (checkout) checkout.hidden = false;

            const recipientEmail = document.getElementById('recipientEmail');
            if (recipientEmail && user.email) {
                recipientEmail.value = user.email;
            }
        } else {
            if (loginRequired) loginRequired.hidden = false;
            if (checkout) checkout.hidden = true;
        }

        renderCart();
    }


    function renderCart() {
        const cart = getCart();

        cartItems.innerHTML = '';

        let totalProducts = 0;
        let subtotal = 0;

        cart.forEach((product, index) => {
            const quantity = Math.max(
                1,
                Number(product.quantity) || 1
            );

            const price = Number(product.price) || 0;

            const productTotal = price * quantity;

            totalProducts += quantity;
            subtotal += productTotal;

            const article = document.createElement('article');

            article.className = 'cart__item';

            const image = document.createElement('img');

            image.className = 'cart__item-image';

            image.src = product.image || '../assets/LogoM.png';

            image.alt = product.name || 'Producto MERCURY';

            image.onerror = () => {
                image.src = '../assets/LogoM.png';
            };

            const info = document.createElement('div');

            info.className = 'cart__item-info';

            const title = document.createElement('h3');

            title.className = 'cart__item-title';

            title.textContent = product.name || 'Producto MERCURY';

            const size = document.createElement('p');

            size.className = 'cart__item-detail';

            size.textContent =
                'Talla: ' + (product.size || 'No especificada');

            const priceText = document.createElement('p');

            priceText.className = 'cart__item-price';

            priceText.textContent = currency.format(productTotal);

            const quantityControls = document.createElement('div');

            quantityControls.className = 'cart__item-quantity';

            const decrease = document.createElement('button');

            decrease.type = 'button';
            decrease.className = 'cart__quantity-btn';
            decrease.textContent = '−';
            decrease.dataset.action = 'decrease';
            decrease.dataset.index = index;

            const quantityText = document.createElement('span');

            quantityText.textContent = quantity;

            const increase = document.createElement('button');

            increase.type = 'button';
            increase.className = 'cart__quantity-btn';
            increase.textContent = '+';
            increase.dataset.action = 'increase';
            increase.dataset.index = index;

            quantityControls.append(
                decrease,
                quantityText,
                increase
            );

            const remove = document.createElement('button');

            remove.type = 'button';
            remove.className = 'cart__item-remove';
            remove.textContent = 'Eliminar producto';
            remove.dataset.action = 'remove';
            remove.dataset.index = index;

            info.append(
                title,
                size,
                priceText,
                quantityControls,
                remove
            );

            article.append(image, info);

            cartItems.appendChild(article);
        });

        const shipping = totalProducts > 0 ? SHIPPING_PRICE : 0;

        const total = subtotal + shipping;

        if (cartCount) cartCount.textContent = totalProducts;

        if (productCount) {
            productCount.textContent =
                totalProducts +
                (totalProducts === 1 ? ' PRODUCTO' : ' PRODUCTOS');
        }

        if (subtotalElement) {
            subtotalElement.textContent = currency.format(subtotal);
        }

        if (shippingElement) {
            shippingElement.textContent =
                shipping === 0 ? 'Gratis' : currency.format(shipping);
        }

        if (totalElement) {
            totalElement.textContent = currency.format(total);
        }

        if (cartEmpty) cartEmpty.hidden = totalProducts > 0;

        cartItems.hidden = totalProducts === 0;

        if (checkoutForm) {
            checkoutForm.hidden = totalProducts === 0;
        }

        if (confirmButton) {
            confirmButton.disabled = totalProducts === 0;
        }
    }


    /* Modificar productos */

    cartItems.addEventListener('click', event => {
        const button = event.target.closest('button[data-action]');

        if (!button) return;

        const index = Number(button.dataset.index);

        const action = button.dataset.action;

        const cart = getCart();

        if (!cart[index]) return;

        if (action === 'increase') {
            cart[index].quantity =
                (Number(cart[index].quantity) || 1) + 1;
        }

        if (action === 'decrease') {
            const quantity = Number(cart[index].quantity) || 1;

            if (quantity > 1) {
                cart[index].quantity = quantity - 1;
            } else {
                cart.splice(index, 1);
            }
        }

        if (action === 'remove') {
            cart.splice(index, 1);
        }

        saveCart(cart);

        renderCart();
    });


    /* Finalizar compra */

    if (checkoutForm) {
        checkoutForm.addEventListener('submit', event => {
            event.preventDefault();

            feedback.textContent = '';
            feedback.style.color = '';

            if (!getCurrentUser()) {
                feedback.textContent =
                    'Debes iniciar sesión para completar tu compra.';
                return;
            }

            const cart = getCart();

            if (cart.length === 0) {
                feedback.textContent =
                    'No tienes productos en tu carrito.';
                return;
            }

            if (!checkoutForm.reportValidity()) return;
            const recipient = {
                name: document.getElementById('recipientName').value.trim(),
                email: document.getElementById('recipientEmail').value.trim(),
                phone: document.getElementById('recipientPhone').value.trim(),
                address: document.getElementById('address').value.trim(),
                number: document.getElementById('addressNumber').value.trim(),
                postalCode: document.getElementById('postalCode').value.trim(),
                city: document.getElementById('city').value.trim(),
                province: document.getElementById('province').value.trim(),
                notes: document.getElementById('addressNotes').value.trim()
            };

            const subtotal = cart.reduce((sum, product) => {
                return sum +
                    (Number(product.price) || 0) *
                    (Number(product.quantity) || 1);

            }, 0);

            const order = {
                recipient: recipient,
                products: cart,
                total: subtotal + SHIPPING_PRICE,
                date: new Date().toISOString()
            };

            console.log('Pedido preparado:', order);

            feedback.textContent =
                'Formulario validado. El siguiente paso es conectar el backend y la pasarela de pago.';

            feedback.style.color = '#16845b';
        });
    }

    document.addEventListener('cartUpdated', renderCart);

    checkSession();
});


/* PERSONALIZADOR MERCURY */

document.addEventListener('DOMContentLoaded', () => {
    const stage = document.getElementById('customizerStage');

    if (!stage) return;
    const shoePreview = document.getElementById('shoePreview');
    const sockPreview = document.getElementById('sockPreview');

    const stageCaption = document.getElementById('stageCaption');

    const priceValue = document.getElementById('priceValue');

    const colorPalette = document.getElementById('colorPalette');

    const selectedColorLabel =
        document.getElementById('selectedColorLabel');

    const designSummary = document.getElementById('designSummary');

    const feedback = document.getElementById('feedback');

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


    /* Estado inicial */

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

    let state = JSON.parse(JSON.stringify(initialState));


    function getActiveColors() {
        return state.product === 'sock'
            ? state.sockColors
            : state.colors;
    }


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


    /* Mostrar producto */

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

            const selected =
                button.dataset.product === state.product;

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


    /* Paleta de colores */

    function renderPalette() {
        const activeColors = getActiveColors();

        const currentColor =
            activeColors[state.zone] || '#f4f4f5';

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
                button.classList.add(
                    'customizer__swatch--selected'
                );
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


    /* Aplicar colores */

    function renderColors() {
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


    /* Precio */

    function getProductPrice() {
        if (state.product === 'sock') return 12.99;

        if (state.product === 'set') return 99.99;

        return 89.99;
    }


    function renderPrice() {
        priceValue.textContent =
            `${getProductPrice().toFixed(2).replace('.', ',')} €`;
    }


    /* Resumen */

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


    /* Cambiar diseño */

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

                main: '#f4f4f5',
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


    /* Cambiar producto */

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


    /* Seleccionar zona */

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


    /* Seleccionar diseño */

    document.querySelectorAll('[data-design]').forEach(button => {
        button.addEventListener('click', () => {
            setDesign(button.dataset.design);
        });
    });


    /* Restablecer */

    const resetButton = document.getElementById('resetButton');

    if (resetButton) {
        resetButton.addEventListener('click', () => {
            state = JSON.parse(JSON.stringify(initialState));
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


    /* Guardar diseño */

    const saveButton = document.getElementById('saveButton');

    if (saveButton) {
        saveButton.addEventListener('click', () => {

            const productNames = {

                shoe: 'Zapatillas personalizadas',
                sock: 'Calcetines personalizados',
                set: 'Conjunto personalizado'
            };

            const customization = {

                product: state.product,
                design: state.design,
                colors: JSON.parse(JSON.stringify(state.colors)),
                sockColors: JSON.parse(JSON.stringify(state.sockColors))
            };

            const product = {

                id: 'custom-' + Date.now(),
                name: productNames[state.product],
                price: getProductPrice(),
                size: 'Personalizado',
                image: '',
                customization: customization
            };

            addProductToCart(product);

            feedback.textContent =
                '¡Diseño añadido correctamente al carrito!';

        });
    }


    /* Inicializar */

    if (
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


/* NEWSLETTER */

document.addEventListener('DOMContentLoaded', () => {
    const newsletterForm =
        document.getElementById('newsletterForm');

    const newsletterFeedback =
        document.getElementById('newsletterFeedback');

    if (newsletterForm) {
        newsletterForm.addEventListener('submit', event => {

            event.preventDefault();

            if (newsletterFeedback) {
                newsletterFeedback.classList.add(
                    'newsletter__feedback--success'
                );
            }

            newsletterForm.reset();

            setTimeout(() => {
                if (newsletterFeedback) {
                    newsletterFeedback.classList.remove(
                        'newsletter__feedback--success'
                    );
                }
            }, 4000);
        });
    }

});
