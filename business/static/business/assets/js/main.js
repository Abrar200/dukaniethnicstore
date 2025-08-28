// Table of contents
/**** Select language, money top nav ****/
/**** Add fixed header ****/
/**** Marquee banner top ****/
/**** Menu mobile ****/
/**** Modal Newsletter ****/
/**** Modal Search ****/
/**** Redirect to search-results when enter or click form search ****/
/**** Filter product in search-results ****/
/**** Modal login ****/
/**** initialize the variable(cart, wishlist, compare) in local storage ****/
/**** Modal Wishlist ****/
/**** handleItemModalWishlist ****/
/**** Modal Cart ****/
/**** handleItemModalCart ****/
/**** sub-menu-department ****/
/**** Open note, shipping, coupon popup ****/
/**** Banner top ****/
/**** Slider ****/
/**** Slider Toys kid ****/
/**** Change active menu tab ****/
/**** Countdown time ****/
/**** Collection, Trending ****/
/**** list-product ****/
/**** list-three-product ****/
/**** Lookbook Underwear ****/
/**** list-feature-product Underwear ****/
/**** Modal Compare ****/
/**** handleItemModalCompare ****/
/**** Modal Quickview ****/
/**** handleItemModalQuickview ****/
/**** show information about product in modalQuickview ****/
/**** Modal SizeGuide ****/
/**** Create product item ****/
/**** addEventToProductItem ****/
/**** Change product img when active color in list color ****/
/**** filter product img in home6, product detail ****/
/**** Fetch products from JSON file (assuming products.json) ****/
/**** fetch product in marketplace ****/
/**** Featured product underwear ****/
/**** redirect to blog detail ****/
/**** list-testimonial ****/
/**** list-instagram ****/
/**** list-brand ****/
/**** Before After Cosmetic1 ****/
/**** Change active video cosmetic2 ****/
/**** Modal Video ****/
/**** Scroll to top ****/
/**** Handle layout cols in list product wishlist page, shop ****/
/**** Display wishlist, cart, compare item from localStorage ****/
/**** faqs ****/


// Select language, currency top nav
const chooseType = document.querySelectorAll(".top-nav .choose-type");
const optionItems = document.querySelectorAll(".top-nav .choose-type .list-option li");

if (chooseType) {
  chooseType.forEach(item => {
    item.addEventListener('click', () => {
      item.querySelector('.list-option').classList.toggle('open')
    })
  })

  optionItems.forEach(item => {
    item.addEventListener('click', () => {
      item.parentElement.querySelector('.active').classList.remove('active')
      item.classList.add('active')

      let dataItem = item.getAttribute('data-item')
      item.parentElement.parentElement.querySelector('.selected').innerHTML = dataItem
      item.closest('choose-type').classList.remove('open')
    })
  })
}




// Add fixed header
const headerMain = document.querySelector(".header-menu");

window.addEventListener("scroll", () => {
  if (window.scrollY > 100) {
    headerMain.classList.add("fixed");
  } else {
    headerMain.classList.remove("fixed");
  }
});

// Marquee banner top
let SwiperTop = new Swiper(".marquee-block", {
  spaceBetween: 0,
  centeredSlides: true,
  speed: 5000,
  autoplay: {
    delay: 1,
  },
  loop: true,
  slidesPerView: "auto",
  allowTouchMove: false,
  disableOnInteraction: true,
});

// Menu mobile
const menuMobileIcon = document.querySelector(".menu-mobile-icon");
const menuMobileBlock = document.querySelector("#menu-mobile");
const closeMenuMobileIcon = document.querySelector(
  "#menu-mobile .close-menu-mobile-btn"
);

const openMenuMobile = () => {
  menuMobileBlock.classList.add("open");
};

const closeMenuMobile = () => {
  menuMobileBlock.classList.remove("open");
};

if (menuMobileIcon) {
  menuMobileIcon.addEventListener("click", openMenuMobile);
  closeMenuMobileIcon.addEventListener("click", closeMenuMobile);
}

const mobileNavItems = document.querySelectorAll(
  "#menu-mobile .list-nav>ul>li"
);

mobileNavItems.forEach((item) => {
  item.addEventListener("click", () => {
    if (!item.classList.contains("open")) {
      item.classList.add("open");
    }
  });
});

const backMenuBtns = document.querySelectorAll(
  "#menu-mobile .list-nav>ul>li .back-btn"
);

backMenuBtns.forEach((btn) => {
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    const subNavParent = btn.parentElement.parentElement;
    subNavParent.classList.remove("open");
  });
});

// Modal Newsletter
const modalNewsletter = document.querySelector(".modal-newsletter");
const modalNewsletterMain = document.querySelector(
  ".modal-newsletter .modal-newsletter-main"
);
const closeBtnModalNewsletter = document.querySelector(".modal-newsletter .close-newsletter-btn");


if (modalNewsletter) {
  setTimeout(() => {
    modalNewsletterMain.classList.add('open')
  }, 3000);

  modalNewsletter.addEventListener('click', () => {
    modalNewsletterMain.classList.remove('open')
  })

  closeBtnModalNewsletter.addEventListener('click', () => {
    modalNewsletterMain.classList.remove('open')
  })

  modalNewsletterMain.addEventListener('click', (e) => {
    e.stopPropagation()
  })
}

// Modal Search
const searchIcon = document.querySelector(".search-icon");
const modalSearch = document.querySelector(".modal-search-block");
const modalSearchMain = document.querySelector(
  ".modal-search-block .modal-search-main"
);

if (searchIcon) {
  searchIcon.addEventListener("click", () => {
    modalSearchMain.classList.add("open");
  });

  modalSearch.addEventListener("click", () => {
    modalSearchMain.classList.remove("open");
  });

  modalSearchMain.addEventListener("click", (e) => {
    e.stopPropagation();
  });
}

// Redirect to search-results when enter or click form search
const formSearch = document.querySelectorAll(".form-search");

if (formSearch) {
  formSearch.forEach((form) => {
    const formInput = form.querySelector("input");
    const searchIcon = form.querySelector("i.ph-magnifying-glass");
    const searchBtn = form.querySelector("button");

    formInput.addEventListener("keyup", (e) => {
      if (e.key === "Enter") {
        window.location.href = `search-result.html?query=${formInput.value}`;
      }
    });

    if (searchIcon) {
      searchIcon.addEventListener("click", (e) => {
        window.location.href = `search-result.html?query=${formInput.value}`;
      });
    }

    if (searchBtn) {
      searchBtn.addEventListener("click", (e) => {
        window.location.href = `search-result.html?query=${formInput.value}`;
      });
    }
  });
}

const keywordSearch = document.querySelectorAll(".list-keyword .item");

if (keywordSearch) {
  keywordSearch.forEach((item) => {
    item.addEventListener("click", (e) => {
      const query = item.innerHTML.toLowerCase().replace(/\s+/g, "");
      window.location.href = `search-result.html?query=${query}`;
    });
  });
}

// Filter product in search-results
const listSearchResults = document.querySelector(".search-result-block");

if (listSearchResults) {
  // get curent URL
  const urlParams = new URLSearchParams(window.location.search);

  // get value 'query'
  const queryValue = urlParams.get("query");

  const listProductResult = document.querySelector(".list-product-result");
  if (queryValue) {
    fetch("./assets/data/Product.json")
      .then((response) => response.json())
      .then((products) => {
        const filterPrd = products.filter(
          (product) =>
            product.type.includes(queryValue) ||
            product.category.includes(queryValue) ||
            product.name.includes(queryValue)
        );
        const result = listSearchResults.querySelectorAll(".result");
        const resultQuantity =
          listSearchResults.querySelector(".result-quantity");

        // Set number of results
        resultQuantity.innerHTML = filterPrd.length;

        // Set text result
        result.forEach((item) => {
          item.innerHTML = queryValue;
        });

        // Show product results
        filterPrd.forEach((product) => {
          const productElement = createProductItem(product);
          listProductResult.appendChild(productElement);
        });

        if (filterPrd.length === 0) {
          listProductResult.innerHTML = `<p>No product found.</p>`;
        }
      })
      .catch((error) => console.error("Error loading products:", error));
  } else {
    listProductResult.innerHTML = `<p>No product searched.</p>`;
  }
}

// Modal login
const loginIcon = document.querySelector(".user-icon i");
const loginPopup = document.querySelector(".login-popup");

loginIcon?.addEventListener("click", () => {
  loginPopup.classList.toggle("open");
});

// initialize the variable(cart, wishlist, compare) in local storage


let wishlistStore = localStorage.getItem("wishlistStore");
if (wishlistStore === null) {
  localStorage.setItem("wishlistStore", JSON.stringify([]));
}

let compareStore = localStorage.getItem("compareStore");
if (compareStore === null) {
  localStorage.setItem("compareStore", JSON.stringify([]));
}

let quickViewStore = localStorage.getItem("quickViewStore");
if (quickViewStore === null) {
  localStorage.setItem("quickViewStore", JSON.stringify([]));
}




// Modal Cart
const cartIcon = document.querySelector(".cart-icon");
const modalCart = document.querySelector(".modal-cart-block");
const modalCartMain = document.querySelector(".modal-cart-block .modal-cart-main");
const closeCartIcon = document.querySelector(".modal-cart-main .close-btn");
const continueCartIcon = document.querySelector(".modal-cart-main .continue");
const addCartBtns = document.querySelectorAll(".add-cart-btn");

const openModalCart = () => {
  modalCartMain.classList.add("open");
};

const closeModalCart = () => {
  modalCartMain.classList.remove("open");
};

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

const csrftoken = getCookie('csrftoken');


const addToCart = (productId) => {
  const product_id = productId;
  console.log('Product ID:', product_id);

  fetch('/cart/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({ product_id }),
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to add product to cart');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        console.log('Product added successfully:', data);
        updateCartModalContent(); // Ensure this function is called immediately after adding the product
        openModalCart();
      }
    })
    .catch(error => console.error('Error:', error));
};




document.addEventListener("DOMContentLoaded", function() {
  const plusIcons = document.querySelectorAll(".ph-plus");
  const minusIcons = document.querySelectorAll(".ph-minus");
  const colorItems = document.querySelectorAll(".color-item");
  const sizeItems = document.querySelectorAll(".size-item");
  const addCartBtns = document.querySelectorAll(".add-cart-btn");
  const cartIcon = document.querySelector(".cart-icon");
  const modalCart = document.querySelector(".modal-cart-block");
  const modalCartMain = document.querySelector(".modal-cart-main");
  const closeCartIcon = document.querySelector(".close-btn");
  const continueCartIcon = document.querySelector(".continue");
  let selectedColorId = null;
  let selectedSizeId = null;

  const openModalCart = () => {
      modalCartMain.classList.add("open");
      modalCart.classList.add("open");
  };

  const closeModalCart = () => {
      modalCartMain.classList.remove("open");
      modalCart.classList.remove("open");
  };

  // Add event listeners to color items
  colorItems.forEach(item => {
      item.addEventListener("click", function() {
          // Remove 'active' class from all color items
          colorItems.forEach(i => i.classList.remove("active"));
          // Add 'active' class to the clicked color item
          item.classList.add("active");
          // Update selected color ID and display text
          selectedColorId = item.dataset.variationId;
          document.getElementById("selected-color").innerText = `Color: ${item.dataset.color}`;
      });
  });

  // Add event listeners to size items
  sizeItems.forEach(item => {
      item.addEventListener("click", function() {
          // Remove 'active' class from all size items
          sizeItems.forEach(i => i.classList.remove("active"));
          // Add 'active' class to the clicked size item
          item.classList.add("active");
          // Update selected size ID and display text
          selectedSizeId = item.dataset.variationId;
          document.getElementById("selected-size").innerText = `Size: ${item.dataset.size}`;
      });
  });

  plusIcons.forEach(icon => {
      icon.addEventListener("click", function() {
          const itemId = icon.dataset.itemId;
          updateQuantity(itemId, 'increase');
      });
  });

  minusIcons.forEach(icon => {
      icon.addEventListener("click", function() {
          const itemId = icon.dataset.itemId;
          updateQuantity(itemId, 'decrease');
      });
  });

  function updateQuantity(itemId, action) {
      fetch('/cart/update_quantity/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken,
          },
          body: JSON.stringify({ item_id: itemId, action: action }),
      })
      .then(response => {
          if (!response.ok) {
              throw new Error('Failed to update quantity');
          }
          return response.json();
      })
      .then(data => {
          if (data.success) {
              updateCartModalContent();
          }
      })
      .catch(error => console.error('Error:', error));
  }

  addCartBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
          const productId = btn.dataset.productId;
          addToCart(productId, selectedColorId, selectedSizeId);
      });
  });

  cartIcon.addEventListener("click", openModalCart);
  closeCartIcon.addEventListener("click", closeModalCart);
  continueCartIcon.addEventListener("click", closeModalCart);
  modalCart.addEventListener("click", closeModalCart);
  modalCartMain.addEventListener("click", (e) => {
      e.stopPropagation();
  });

  const addToCart = (productId, colorId, sizeId) => {
      const product_id = productId;
      const selected_variations = [];
      if (colorId) selected_variations.push(colorId);
      if (sizeId) selected_variations.push(sizeId);

      fetch('/cart/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken,
          },
          body: JSON.stringify({ product_id, selected_variations }),
      })
      .then(response => {
          if (!response.ok) {
              throw new Error('Failed to add product to cart');
          }
          return response.json();
      })
      .then(data => {
          if (data.success) {
              updateCartModalContent();
              openModalCart();
          }
      })
      .catch(error => console.error('Error:', error));
  };

  function updateCartModalContent() {
      console.log('Updating cart modal content...');
      fetchCartData()
      .then((cartData) => {
          console.log('Cart data fetched:', cartData);
          const cartItemsContainer = document.querySelector('.modal-cart-main .list-product');
          cartItemsContainer.innerHTML = '';

          if (cartData.items.length === 0) {
              cartItemsContainer.innerHTML = '<p class="mt-1">No product in cart</p>';
          } else {
              cartData.items.forEach((item) => {
                  const cartItem = createCartItemElement(item);
                  cartItemsContainer.appendChild(cartItem);
              });
          }

          const subtotalElement = document.querySelector('.modal-cart-main .total-price');
          const subtotal = parseFloat(cartData.subtotal) || 0;
          subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
      });
  }

  function fetchCartData() {
      return fetch('/cart/data/')
      .then((response) => response.json())
      .then((data) => data);
  }

  function createCartItemElement(item) {
      console.log('Creating cart item element for:', item);
      const cartItemElement = document.createElement('div');
      cartItemElement.classList.add('item', 'py-5', 'flex', 'items-center', 'justify-between', 'gap-3', 'border-b', 'border-line');
      cartItemElement.dataset.item = item.id;

      const imageUrl = item.product.image || '/static/path/to/default-image.png';

      cartItemElement.innerHTML = `
          <div class="infor flex items-center gap-3 w-full">
              <div class="bg-img w-[100px] aspect-square flex-shrink-0 rounded-lg overflow-hidden">
                  <img src="${imageUrl}" alt="product" class="w-full h-full">
              </div>
              <div class="w-full">
                  <div class="flex items-center justify-between w-full">
                      <div class="name text-button">${item.product.name}</div>
                  </div>
                  <div class="flex items-center justify-between gap-2 mt-3 w-full">
                      <div class="flex items-center text-secondary2 capitalize">
                          ${item.variations.join(' / ')}
                      </div>
                      <div class="product-price text-title">$${item.product.price}</div>
                  </div>
              </div>
          </div>
      `;

      return cartItemElement;
  }
});


// Countdown cart
let timeLeft = 600;
const countDownCart = setInterval(function () {
  let minutes = Math.floor(timeLeft / 60);
  if (minutes / 10 < 1) {
    minutes = `0${minutes}`;
  }

  let seconds = timeLeft % 60;
  if (seconds / 10 < 1) {
    seconds = `0${seconds}`;
  }

  const minuteTime = document.querySelector(".countdown-cart .minute");
  const secondTime = document.querySelector(".countdown-cart .second");

  if (minuteTime) {
    minuteTime.innerHTML = minutes;
  }
  if (secondTime) {
    secondTime.innerHTML = seconds;
  }

  timeLeft--;

  if (timeLeft < 0) {
    timeLeft = 600;
  }
}, 1000);

// Open note, shipping, coupon popup
const noteBtn = modalCart.querySelector(".note-btn");
const shippingBtn = modalCart.querySelector(".shipping-btn");
const couponBtn = modalCart.querySelector(".coupon-btn");
const notePopup = modalCart.querySelector(".note-block");
const shippingPopup = modalCart.querySelector(".shipping-block");
const couponPopup = modalCart.querySelector(".coupon-block");

if (modalCart) {
  // note block
  noteBtn.addEventListener("click", () => {
    notePopup.classList.toggle("active");
  });

  notePopup.querySelector(".button-main").addEventListener("click", () => {
    notePopup.classList.remove("active");
  });

  notePopup.querySelector(".cancel-btn").addEventListener("click", () => {
    notePopup.classList.remove("active");
  });

  // shipping block
  shippingBtn.addEventListener("click", () => {
    shippingPopup.classList.toggle("active");
  });

  shippingPopup.querySelector(".button-main").addEventListener("click", () => {
    shippingPopup.classList.remove("active");
  });

  shippingPopup.querySelector(".cancel-btn").addEventListener("click", () => {
    shippingPopup.classList.remove("active");
  });

  // coupon block
  couponBtn.addEventListener("click", () => {
    couponPopup.classList.toggle("active");
  });

  couponPopup.querySelector(".button-main").addEventListener("click", () => {
    couponPopup.classList.remove("active");
  });

  couponPopup.querySelector(".cancel-btn").addEventListener("click", () => {
    couponPopup.classList.remove("active");
  });
}

// sub-menu-department
const menuDepartmentBtn = document.querySelector(".menu-department-btn");
const subMenuDepartment = document.querySelector(".sub-menu-department");

if (menuDepartmentBtn) {
  menuDepartmentBtn.addEventListener("click", () => {
    subMenuDepartment.classList.toggle("open");
  });
}

// sub-menu-category
const menuCategoryBtn = document.querySelector(".category-block .category-btn");
const subMenuCategory = document.querySelector(
  ".category-block .sub-menu-category"
);

if (menuCategoryBtn) {
  menuCategoryBtn.addEventListener("click", () => {
    subMenuCategory.classList.toggle("open");
  });
}

// Banner top
var swiperBannerTop = new Swiper(".swiper-banner-top", {
  spaceBetween: 0,
  slidesPerView: 1,
  navigation: {
    prevEl: ".swiper-button-custom-prev",
    nextEl: ".swiper-button-custom-next",
  },
  loop: true,
  autoplay: {
    delay: 5000,
    disableOnInteraction: false,
  },
});

// Slider
var swiperSlider = new Swiper(".swiper-slider", {
  spaceBetween: 0,
  slidesPerView: 1,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  loop: true,
  autoplay: {
    delay: 4000,
    disableOnInteraction: false,
  },
});

// Slider Toys kid
if (document.querySelector(".slider-toys-kid")) {
  $(".slider-toys-kid").slick({
    dots: false,
    arrows: false,
    infinite: true,
    speed: 300,
    autoplay: false,
    autoplaySpeed: 4000,
    slidesToShow: 1,
    slidesToScroll: 1,
    touchThreshold: 100,
    draggable: true,
    useTransform: false,
  });
}

// Change active menu tab
const tabItems = document.querySelectorAll(".menu-tab .tab-item");
const itemActive = document.querySelectorAll(".menu-tab .tab-item.active");

itemActive.forEach((item) => {
  let indicator = item.parentElement.querySelector(".indicator");
  if (indicator) {
    indicator.style.width = item.getBoundingClientRect().width + "px";
    indicator.style.left =
      item.getBoundingClientRect().left -
      item.parentElement.getBoundingClientRect().left +
      "px";
  }
});

tabItems.forEach((item) => {
  item.addEventListener("click", () => {
    let indicator = item.parentElement.querySelector(".indicator");
    if (indicator) {
      indicator.style.width = item.getBoundingClientRect().width + "px";
      indicator.style.left =
        item.getBoundingClientRect().left -
        item.parentElement.getBoundingClientRect().left +
        "px";
    }

    if (item.parentElement.querySelector(".active")) {
      item.parentElement.querySelector(".active").classList.remove("active");
    }
    item.classList.add("active");
  });
});

// Countdown time
const countDown = new Date("June 30, 2024 00:00:00").getTime();
const setCountDown = setInterval(function () {
  let now = new Date().getTime();
  let distance = countDown - now;

  let days = Math.floor(distance / (1000 * 60 * 60 * 24));
  if (days / 10 < 1) {
    days = `0${days}`;
  }

  let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  if (hours / 10 < 1) {
    hours = `0${hours}`;
  }

  let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  if (minutes / 10 < 1) {
    minutes = `0${minutes}`;
  }

  let seconds = Math.floor((distance % (1000 * 60)) / 1000);
  if (seconds / 10 < 1) {
    seconds = `0${seconds}`;
  }

  const dayTime = document.querySelectorAll(".countdown-day");
  const hourTime = document.querySelectorAll(".countdown-hour");
  const minuteTime = document.querySelectorAll(".countdown-minute");
  const secondTime = document.querySelectorAll(".countdown-second");

  if (dayTime) {
    dayTime.forEach((time) => {
      time.innerHTML = days;
    });
  }
  if (hourTime) {
    hourTime.forEach((time) => {
      time.innerHTML = hours;
    });
  }
  if (minuteTime) {
    minuteTime.forEach((time) => {
      time.innerHTML = minutes;
    });
  }
  if (secondTime) {
    secondTime.forEach((time) => {
      time.innerHTML = seconds;
    });
  }

  if (distance < 0) {
    clearInterval(x);
    if (dayTime) {
      dayTime.forEach((time) => {
        time.innerHTML = "00";
      });
    }
    if (hourTime) {
      hourTime.forEach((time) => {
        time.innerHTML = "00";
      });
    }
    if (minuteTime) {
      minuteTime.forEach((time) => {
        time.innerHTML = "00";
      });
    }
    if (secondTime) {
      secondTime.forEach((time) => {
        time.innerHTML = "00";
      });
    }
  }
}, 1000);

// Collection
if (document.querySelector(".swiper-collection")) {
  var swiperCollection = new Swiper(".swiper-collection", {
    navigation: {
      prevEl: ".swiper-button-prev",
      nextEl: ".swiper-button-next",
    },
    loop: true,
    autoplay: {
      delay: 3500,
      disableOnInteraction: false,
    },
    slidesPerView: 2,
    spaceBetween: 16,
    breakpoints: {
      640: {
        slidesPerView: 3,
        spaceBetween: 16,
      },
      768: {
        slidesPerView: 3,
        spaceBetween: 20,
      },
      1280: {
        slidesPerView: 4,
        spaceBetween: 20,
      },
    },
  });
}

// Collection 6
if (document.querySelector(".swiper-collection-scroll")) {
  var swiperCollection = new Swiper(".swiper-collection-scroll", {
    scrollbar: {
      el: ".swiper-scrollbar",
      hide: true,
    },
    loop: true,
    slidesPerView: 2,
    spaceBetween: 16,
    breakpoints: {
      640: {
        slidesPerView: 3,
        spaceBetween: 16,
      },
      768: {
        slidesPerView: 3,
        spaceBetween: 20,
      },
      1280: {
        slidesPerView: 4,
        spaceBetween: 20,
      },
    },
  });
}

// Popular product 6
var swiperScrollImg = new Swiper(".swiper-img-scroll", {
  scrollbar: {
    el: ".swiper-scrollbar",
    hide: true,
  },
  loop: false,
  slidesPerView: 2,
  spaceBetween: 16,
  breakpoints: {
    640: {
      slidesPerView: 3,
      spaceBetween: 16,
    },
    1024: {
      slidesPerView: 2,
      spaceBetween: 20,
    },
  },
});

// Trending 7
if (document.querySelector(".swiper-list-trending")) {
  var swiperCollection = new Swiper(".swiper-list-trending", {
    navigation: {
      prevEl: ".swiper-button-prev",
      nextEl: ".swiper-button-next",
    },
    loop: true,
    autoplay: {
      delay: 3500,
      disableOnInteraction: false,
    },
    slidesPerView: 2,
    spaceBetween: 16,
    breakpoints: {
      640: {
        slidesPerView: 3,
        spaceBetween: 16,
      },
      768: {
        slidesPerView: 4,
        spaceBetween: 20,
      },
      1024: {
        slidesPerView: 5,
        spaceBetween: 20,
      },
      1280: {
        slidesPerView: 6,
        spaceBetween: 30,
      },
    },
  });
}

// Collection 8
if (document.querySelector(".swiper-collection-eight")) {
  var swiperCollection = new Swiper(".swiper-collection-eight", {
    navigation: {
      prevEl: ".swiper-button-prev",
      nextEl: ".swiper-button-next",
    },
    loop: true,
    autoplay: {
      delay: 3500,
      disableOnInteraction: false,
    },
    slidesPerView: 2,
    spaceBetween: 16,
    breakpoints: {
      640: {
        slidesPerView: 3,
        spaceBetween: 16,
      },
      768: {
        slidesPerView: 3,
        spaceBetween: 20,
      },
      1024: {
        slidesPerView: 4,
        spaceBetween: 20,
      },
      1280: {
        slidesPerView: 5,
        spaceBetween: 30,
      },
    },
  });
}

// list-product
if (document.querySelector(".swiper-list-product")) {
  var swiperListProduct = new Swiper(".swiper-list-product", {
    navigation: {
      prevEl: ".swiper-button-prev2",
      nextEl: ".swiper-button-next2",
    },
    loop: true,
    slidesPerView: 2,
    spaceBetween: 16,
    breakpoints: {
      640: {
        slidesPerView: 3,
        spaceBetween: 16,
      },
      768: {
        slidesPerView: 3,
        spaceBetween: 30,
      },
      1280: {
        slidesPerView: 4,
        spaceBetween: 30,
      },
    },
  });
}

// list-three-product
if (document.querySelector(".swiper-list-three-product")) {
  var swiperListProduct = new Swiper(".swiper-list-three-product", {
    navigation: {
      prevEl: ".swiper-button-prev2",
      nextEl: ".swiper-button-next2",
    },
    loop: true,
    slidesPerView: 2,
    spaceBetween: 16,
    breakpoints: {
      640: {
        slidesPerView: 3,
        spaceBetween: 16,
      },
      768: {
        slidesPerView: 3,
        spaceBetween: 30,
      },
      1280: {
        slidesPerView: 3,
        spaceBetween: 30,
      },
    },
  });
}

// Lookbook Underwear
const lookbookUnderwear = document.querySelector('.lookbook-underwear')

if (lookbookUnderwear) {
  fetch("./assets/data/Product.json")
    .then((response) => response.json())
    .then((products) => {
      const itemDot = lookbookUnderwear.querySelector('.list-img .item .dots')
      const itemDots = lookbookUnderwear.querySelectorAll('.list-img .item .dots')
      const listPrd = lookbookUnderwear.querySelector('.list-product')
      const prdId = itemDot.getAttribute('data-item');

      // Display products
      products
        .filter((product) => product.id === prdId)
        .forEach((product) => {
          const productElement = createProductItem(product);
          listPrd.appendChild(productElement);
        });

      itemDots.forEach(item => {
        item.addEventListener('click', () => {
          const prdId = item.getAttribute('data-item');

          // Display products
          listPrd.innerHTML = ''

          products
            .filter((product) => product.id === prdId)
            .forEach((product) => {
              const productElement = createProductItem(product);
              listPrd.appendChild(productElement);
              addEventToProductItem()
            });
        })
      })
    })
    .catch((error) => console.error("Error loading products:", error));
}

// list-feature-product Underwear
var swiperUnderwear = new Swiper(".mySwiper", {
  spaceBetween: 0,
  slidesPerView: 1,
  // freeMode: true,
  watchSlidesProgress: true,
});
var swiper2 = new Swiper(".mySwiper2", {
  spaceBetween: 0,
  thumbs: {
    swiper: swiperUnderwear,
  },
  on: {
    slideChange: function () {
      // Get index of current slide in swiper 1
      let activeIndex = this.activeIndex;

      // Remove class 'swiper-slide-thumb-active' from all slide in swiper 2
      document.querySelectorAll(".mySwiper .swiper-slide").forEach((slide) => {
        slide.classList.remove("swiper-slide-thumb-active");
      });

      // Add class 'swiper-slide-thumb-active' to slide in swiper 2
      document
        .querySelectorAll(".mySwiper .swiper-slide")
      [activeIndex].classList.add("swiper-slide-thumb-active");
    },
  },
});

// Modal Compare
const modalCompareMain = document.querySelector(
  ".modal-compare-block .modal-compare-main"
);
const closeCompareIcon = document.querySelector(
  ".modal-compare-main .close-btn"
);
const clearCompareIcon = document.querySelector(".modal-compare-main .clear");

const openModalCompare = () => {
  modalCompareMain.classList.add("open");
};

const closeModalCompare = () => {
  modalCompareMain.classList.remove("open");
};

closeCompareIcon.addEventListener("click", closeModalCompare);
clearCompareIcon.addEventListener("click", closeModalCompare);

// Set compare length
const handleItemModalCompare = () => {
  compareStore = localStorage.getItem("compareStore");
  compareStore = compareStore ? JSON.parse(compareStore) : [];

  // Set compare item
  const listItemCompare = document.querySelector(
    ".modal-compare-block .list-product"
  );

  listItemCompare.innerHTML = "";

  if (compareStore.length === 0) {
    listItemCompare.innerHTML = `<p class='mt-1'>No product in compare</p>`;
  } else {
    compareStore.forEach((item) => {
      const prdItem = document.createElement("div");
      prdItem.setAttribute("data-item", item.id);
      prdItem.classList.add(
        "item",
        "p-3",
        "border",
        "border-line",
        "rounded-xl",
        "relative"
      );
      prdItem.innerHTML = `
                <div class="infor flex items-center gap-4">
                    <div class="bg-img w-[100px] h-[100px] flex-shrink-0 rounded-lg overflow-hidden">
                        <img src=${item.thumbImage[0]} alt='img'
                            class='w-full h-full' />
                    </div>
                    <div class=''>
                        <div class="name text-title">${item.name}</div>
                        <div class="product-price text-title mt-2">$${item.price}.00</div>
                    </div>
                </div>
                <div
                    class="remove-btn close-btn absolute w-8 h-8 rounded-full bg-red text-white flex items-center justify-center duration-300 cursor-pointer hover:bg-black"
                    style="top: -16px; right: -16px;"
                    >
                    <i class="ph ph-x text-sm"></i>
                </div>
            `;

      listItemCompare.appendChild(prdItem);
    });
  }

  const prdItems = listItemCompare.querySelectorAll(".item");
  prdItems.forEach((prd) => {
    const removeCompareBtn = prd.querySelector(".remove-btn");
    removeCompareBtn.addEventListener("click", () => {
      const prdId = removeCompareBtn.closest(".item").getAttribute("data-item");
      // compareStore
      const newArray = compareStore.filter((item) => item.id !== prdId);
      localStorage.setItem("compareStore", JSON.stringify(newArray));
      handleItemModalCompare();
      updateCompareIcons();
    });
  });

  const clearCompareBtn = document.querySelector(
    ".modal-compare-block .block-button .clear"
  );
  clearCompareBtn.addEventListener("click", () => {
    localStorage.setItem("compareStore", []);
    updateCompareIcons();
  });
};

const updateCompareIcons = () => {
  const compareIcons = document.querySelectorAll(".compare-btn");
  compareIcons.forEach((compareIcon) => {
    const productId = compareIcon
      .closest(".product-item")
      ?.getAttribute("data-item");
    const compareStore = localStorage.getItem("compareStore")
      ? JSON.parse(localStorage.getItem("compareStore"))
      : [];
    const isProductInCompare = compareStore.some(
      (item) => item.id === productId
    );
    if (isProductInCompare) {
      compareIcon.classList.add("active");
    } else {
      compareIcon.classList.remove("active");
    }
  });
};

handleItemModalCompare();


// Modal QuickView
document.addEventListener("DOMContentLoaded", function() {
  const quickViewButtons = document.querySelectorAll(".quick-view-btn");
  const modalQuickViewBlock = document.querySelector(".modal-quickview-block");
  const closeQuickViewButton = document.querySelector(".modal-quickview-block .close-btn");

  quickViewButtons.forEach(button => {
      button.addEventListener("click", function() {
          const productSlug = button.dataset.productSlug;
          const businessSlug = button.dataset.businessSlug;

          console.log('Quick View Button:', button);
          console.log('Product Slug:', productSlug);
          console.log('Business Slug:', businessSlug);

          if (!productSlug || !businessSlug) {
              console.error('Product Slug or Business Slug is missing');
              return;
          }

          fetch(`/ajax/product/${businessSlug}/${productSlug}/`)
              .then(response => {
                  console.log('Response status:', response.status);
                  if (!response.ok) {
                      throw new Error('Network response was not ok');
                  }
                  return response.json();
              })
              .then(data => {
                  console.log('Data:', data);
                  updateQuickViewModal(data);
                  modalQuickViewBlock.style.display = "block";
              })
              .catch(error => {
                  console.error('Error:', error);
              });
      });
  });

  closeQuickViewButton.addEventListener("click", function() {
      modalQuickViewBlock.style.display = "none";
  });

  modalQuickViewBlock.addEventListener("click", function(event) {
      if (event.target === modalQuickViewBlock) {
          modalQuickViewBlock.style.display = "none";
      }
  });

  function updateQuickViewModal(data) {
      document.getElementById("quickview-name").innerText = data.name;
      document.getElementById("quickview-price").innerText = `$${data.price}`;
      document.getElementById("quickview-description").innerText = data.description;
      document.getElementById("quickview-sku").innerText = data.sku;
      document.getElementById("quickview-categories").innerText = data.categories.join(", ");
      document.getElementById("quickview-tags").innerText = data.tags.join(", ");

      const imagesContainer = document.getElementById("quickview-images");
      imagesContainer.innerHTML = "";
      data.images.forEach(imageUrl => {
          const imgElement = document.createElement("div");
          imgElement.className = "bg-img w-full aspect-[3/4] max-md:w-[150px] max-md:flex-shrink-0 rounded-[20px] overflow-hidden md:mt-6";
          imgElement.innerHTML = `<img src="${imageUrl}" alt="product image" class="w-full h-full object-cover">`;
          imagesContainer.appendChild(imgElement);
      });

      const colorsContainer = document.getElementById("quickview-colors");
      colorsContainer.innerHTML = "";
      data.color_variations.forEach(variation => {
          const colorItem = document.createElement("div");
          colorItem.classList.add("color-item", "w-12", "h-12", "rounded-xl", "duration-300", "relative");
          colorItem.dataset.variationId = variation.values__id;
          colorItem.dataset.color = variation.values__value;

          if (variation.values__image) {
              const imgElement = document.createElement("img");
              imgElement.src = variation.values__image;
              imgElement.alt = "color";
              imgElement.classList.add("rounded-xl");
              colorItem.appendChild(imgElement);
          }

          const tagAction = document.createElement("div");
          tagAction.classList.add("tag-action", "bg-black", "text-white", "caption2", "capitalize", "px-1.5", "py-0.5", "rounded-sm");
          tagAction.innerText = variation.values__value;
          colorItem.appendChild(tagAction);

          colorItem.addEventListener("click", function() {
              colorsContainer.querySelectorAll('.color-item').forEach(i => i.classList.remove('active'));
              colorItem.classList.add('active');
              document.querySelector('#selected-color').innerText = `Color: ${variation.values__value}`;
          });

          colorsContainer.appendChild(colorItem);
      });

      const sizesContainer = document.getElementById("quickview-sizes");
      sizesContainer.innerHTML = "";
      data.size_variations.forEach(variation => {
          const sizeItem = document.createElement("div");
          sizeItem.classList.add("size-item", "w-12", "h-12", "flex", "items-center", "justify-center", "text-button", "rounded-full", "bg-white", "border", "border-line");
          sizeItem.dataset.variationId = variation.values__id;
          sizeItem.dataset.size = variation.values__value;
          sizeItem.innerText = variation.values__value;

          sizeItem.addEventListener("click", function() {
              sizesContainer.querySelectorAll('.size-item').forEach(i => i.classList.remove('active'));
              sizeItem.classList.add('active');
              document.querySelector('#selected-size').innerText = `Size: ${variation.values__value}`;
          });

          sizesContainer.appendChild(sizeItem);
      });
  }
});


// Modal SizeGuide
const openModalSizeGuideBtn = document.querySelectorAll(".size-guide");
const modalSizeGuide = document.querySelector(".modal-sizeguide-block");
const modalSizeGuideMain = document.querySelector(
  ".modal-sizeguide-block .modal-sizeguide-main"
);
const closeSizeGuideIcon = document.querySelector(
  ".modal-sizeguide-main .close-btn"
);

if (modalSizeGuide) {
  const openModalSizeGuide = () => {
    modalSizeGuideMain.classList.add("open");
  };

  const closeModalSizeGuide = () => {
    modalSizeGuideMain.classList.remove("open");
  };

  openModalSizeGuideBtn.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openModalSizeGuide();
    });
  });

  modalSizeGuide.addEventListener("click", closeModalSizeGuide);
  closeSizeGuideIcon.addEventListener("click", closeModalSizeGuide);

  modalSizeGuideMain.addEventListener("click", (e) => {
    e.stopPropagation();
  });

  // Tow bar filter weight height
  const rangeInputSizeguide = document.querySelectorAll(
    ".modal-sizeguide-block .range-input input"
  );
  const progressHeight = document.querySelector(
    ".filter-height .tow-bar-block .progress"
  );
  const progressWeight = document.querySelector(
    ".filter-weight .tow-bar-block .progress"
  );
  const height = document.querySelector(".modal-sizeguide-block .height");
  const weight = document.querySelector(".modal-sizeguide-block .weight");

  rangeInputSizeguide.forEach((input) => {
    input.addEventListener("input", (e) => {
      // set weight, height
      let heightValue = parseInt(rangeInputSizeguide[0].value);
      let weightValue = parseInt(rangeInputSizeguide[1].value);

      height.innerHTML = heightValue;
      weight.innerHTML = weightValue;

      progressHeight.style.right = 100 - (heightValue / 200) * 100 + "%";
      progressWeight.style.right = 100 - (weightValue / 90) * 100 + "%";

      // Change active weight, height
      let sizeItems = document.querySelectorAll(
        ".modal-sizeguide-block .list-size-block .size-item"
      );

      sizeItems.forEach((size) => {
        if (heightValue > 180 || weightValue > 70) {
          if (size.innerHTML.replace(/\s+/g, "") === "2XL") {
            size.classList.add("active");
          } else {
            size.classList.remove("active");
          }
        } else if (heightValue > 170 || weightValue > 60) {
          if (size.innerHTML.replace(/\s+/g, "") === "XL") {
            size.classList.add("active");
          } else {
            size.classList.remove("active");
          }
        } else if (heightValue > 160 || weightValue > 50) {
          if (size.innerHTML.replace(/\s+/g, "") === "L") {
            size.classList.add("active");
          } else {
            size.classList.remove("active");
          }
        } else if (heightValue > 155 || weightValue > 45) {
          if (size.innerHTML.replace(/\s+/g, "") === "M") {
            size.classList.add("active");
          } else {
            size.classList.remove("active");
          }
        } else if (heightValue > 150 || weightValue > 40) {
          if (size.innerHTML.replace(/\s+/g, "") === "S") {
            size.classList.add("active");
          } else {
            size.classList.remove("active");
          }
        } else {
          if (size.innerHTML.replace(/\s+/g, "") === "XS") {
            size.classList.add("active");
          } else {
            size.classList.remove("active");
          }
        }
      });
    });
  });
}

// Create product item
const createProductItem = (product) => {
  const productItem = document.createElement("div");
  productItem.classList.add("product-item", "grid-type");
  productItem.setAttribute("data-item", product.id);

  let productTags = "";
  if (product.new) {
    productTags += `<div class="product-tag text-button-uppercase bg-green px-3 py-0.5 inline-block rounded-full absolute top-3 left-3 z-[1]">New</div>`;
  }
  if (product.sale) {
    productTags += `<div class="product-tag text-button-uppercase text-white bg-red px-3 py-0.5 inline-block rounded-full absolute top-3 left-3 z-[1]">Sale</div>`;
  }

  let productImages = "";
  product.thumbImage.forEach((img, index) => {
    productImages += `<img key="${index}" class="w-full h-full object-cover duration-700" src="${img}" alt="img">`;
  });

  productItem.innerHTML = `
        <div class="product-main cursor-pointer block" data-item="${product.id
    }">
            <div class="product-thumb bg-white relative overflow-hidden rounded-2xl">
                ${productTags}
                <div class="list-action-right absolute top-3 right-3 max-lg:hidden">
                    <div
                        class="add-wishlist-btn w-[32px] h-[32px] flex items-center justify-center rounded-full bg-white duration-300 relative">
                        <div class="tag-action bg-black text-white caption2 px-1.5 py-0.5 rounded-sm">
                            Add To Wishlist</div>
                        <i class="ph ph-heart text-lg"></i>
                    </div>
                    <div
                        class="compare-btn w-[32px] h-[32px] flex items-center justify-center rounded-full bg-white duration-300 relative mt-2">
                        <div class="tag-action bg-black text-white caption2 px-1.5 py-0.5 rounded-sm">
                            Compare Product</div>
                        <i class="ph ph-arrow-counter-clockwise text-lg compare-icon"></i>
                        <i class="ph ph-check-circle text-lg checked-icon"></i>
                    </div>
                </div>
                <div class="product-img w-full h-full aspect-[3/4]">
                    ${productImages}
                </div>
                ${product.sale ? (`
                  <div class="countdown-time-block py-1.5 flex items-center justify-center">
                    <div class="text-xs font-semibold uppercase text-red">
                      <span class='countdown-day'>24</span>
                      <span>D : </span>
                      <span class='countdown-hour'>14</span>
                      <span>H : </span>
                      <span class='countdown-minute'>36</span>
                      <span>M : </span>
                      <span class='countdown-second'>51</span>
                      <span>S</span>
                    </div>
                  </div>
                `) : ''}
                <div class="list-action grid grid-cols-2 gap-3 px-5 absolute w-full bottom-5 max-lg:hidden">
                    <div
                        class="quick-view-btn w-full text-button-uppercase py-2 text-center rounded-full duration-300 bg-white hover:bg-black hover:text-white">
                        Quick View</div>
                        ${product.action === "add to cart"
      ? `
                            <div
                                class="add-cart-btn w-full text-button-uppercase py-2 text-center rounded-full duration-500 bg-white hover:bg-black hover:text-white">
                                Add To Cart
                            </div>
                        `
      : `
                            <div
                                class="quick-shop-btn text-button-uppercase py-2 text-center rounded-full duration-500 bg-white hover:bg-black hover:text-white">
                                Quick Shop</div>
                            <div class="quick-shop-block absolute left-5 right-5 bg-white p-5 rounded-[20px]">
                                <div class="list-size flex items-center justify-center flex-wrap gap-2">
                                    ${product.sizes &&
      product.sizes
        .map(
          (size, index) =>
            `<div key="${index}" class="size-item w-10 h-10 rounded-full flex items-center justify-center text-button bg-white border border-line">${size.trim()}</div>`
        )
        .join("")
      }
                                </div >
    <div class="add-cart-btn button-main w-full text-center rounded-full py-3 mt-4">Add
        To cart</div>
                            </div >
    `
    }
                </div>
            </div>
            <div class="product-infor mt-4 lg:mb-7">
                <div class="product-sold sm:pb-4 pb-2">
                    <div class="progress bg-line h-1.5 w-full rounded-full overflow-hidden relative">
                        <div class='progress-sold bg-red absolute left-0 top-0 h-full' style="width: ${Math.floor(
      (product.sold / product.quantity) * 100
    )}%">
                        </div>
                    </div>
                    <div class="flex items-center justify-between gap-3 gap-y-1 flex-wrap mt-2">
                        <div class="text-button-uppercase">
                            <span class='text-secondary2 max-sm:text-xs'>Sold:
                            </span>
                            <span class='max-sm:text-xs'>${product.sold}</span>
                        </div>
                        <div class="text-button-uppercase">
                            <span class='text-secondary2 max-sm:text-xs'>Available:
                            </span>
                            <span class='max-sm:text-xs'>${product.quantity - product.sold
    }</span>
                        </div>
                    </div>
                </div>
                <div class="product-name text-title duration-300">${product.name
    }</div>
                ${product.variation.length > 0 &&
      product.action === "add to cart"
      ? `
                        <div class="list-color py-2 max-md:hidden flex items-center gap-3 flex-wrap duration-500">
                            ${product.variation
        .map(
          (item, index) =>
            `<div
                                    key="${index}"
                                    class="color-item w-8 h-8 rounded-full duration-300 relative"
                                    style="background-color:${item.colorCode};"
                                >
                                    <div class="tag-action bg-black text-white caption2 capitalize px-1.5 py-0.5 rounded-sm">${item.color}</div>
                                </div>
                                `
        )
        .join("")}
                        </div>`
      : `
                    <div class="list-color list-color-image max-md:hidden flex items-center gap-3 flex-wrap duration-500">
                        ${product.variation
        .map(
          (item, index) =>
            `
                            <div
                                class="color-item w-12 h-12 rounded-xl duration-300 relative"
                                key="${index}"
                            >
                                <img
                                    src="${item.colorImage}"
                                    alt='color'
                                    class='rounded-xl w-full h-full object-cover'
                                />
                                <div class="tag-action bg-black text-white caption2 capitalize px-1.5 py-0.5 rounded-sm">${item.color}</div>
                            </div>
                        `
        )
        .join("")}
                    </div>
                `
    }
        <div
        class="product-price-block flex items-center gap-2 flex-wrap mt-1 duration-300 relative z-[1]">
        <div class="product-price text-title">$${product.price}.00</div>
        ${Math.floor(100 - (product.price / product.originPrice) * 100) > 0
      ? `
                <div class="product-origin-price caption1 text-secondary2">
                    <del>$${product.originPrice}.00</del>
                </div>
                <div
                    class="product-sale caption1 font-medium bg-green px-3 py-0.5 inline-block rounded-full">
                    -${Math.floor(
        100 - (product.price / product.originPrice) * 100
      )}%
                </div>
        `
      : ""
    }
            </div>
        </div>
        </div>
    </div>
    `;

  return productItem;
};




// Active size
const handleActiveSizeChange = () => {
  // List size
  const listSizes = document.querySelectorAll(".list-size");

  listSizes.forEach((list) => {
    const sizeItems = list.querySelectorAll(".size-item");

    sizeItems.forEach((size) => {
      size.addEventListener("click", () => {
        let parent = size.parentElement;
        if (!parent.querySelector(".active")) {
          size.classList.add("active");
        } else {
          parent.querySelector(".active").classList.remove("active");
          size.classList.add("active");
        }
      });
    });

    list.addEventListener("click", (e) => {
      e.stopPropagation();
      const chooseSizeBlock = list.parentElement;
      const sizeSelected = chooseSizeBlock.querySelector(".size");
      const activeSize = list.querySelector(".size-item.active");

      if (sizeSelected && activeSize) {
        sizeSelected.textContent = activeSize.textContent;
      }
    });
  });
}


// Active size
const handleActiveColorChange = () => {
  // List color
  const listColors = document.querySelectorAll(".list-color");

  listColors.forEach((list) => {
    const colorItems = list.querySelectorAll(".color-item");

    colorItems.forEach((color) => {
      color.addEventListener("click", () => {
        let parent = color.parentElement;
        if (!parent.querySelector(".active")) {
          color.classList.add("active");
        } else {
          parent.querySelector(".active").classList.remove("active");
          color.classList.add("active");
        }
      });
    });

    list.addEventListener("click", (e) => {
      e.stopPropagation();
      const chooseColorBlock = list.parentElement;
      const colorSelected = chooseColorBlock.querySelector(".color");
      const activeColor = list.querySelector(".color-item.active .tag-action");

      if (colorSelected && activeColor) {
        colorSelected.textContent = activeColor.textContent;
      }
    });
  });
}


// filter product img in home6, product detail
const filterProductImg = document.querySelector('.filter-product-img')

if (filterProductImg) {
  fetch('./assets/data/Product.json')
    .then(response => response.json())
    .then(data => {
      const prdId = filterProductImg.querySelector('.product-infor').getAttribute('data-item')
      let productMain = data.find(product => product.id === prdId);
      const colorItems = filterProductImg.querySelectorAll('.color-item');

      colorItems.forEach((colorItem) => {
        colorItem.addEventListener('click', () => {
          const selectedColor = colorItem.querySelector('.tag-action').textContent.trim()
          console.log(selectedColor);
          const selectedVariation = productMain.variation.find(variation => variation.color === selectedColor);
          console.log(selectedVariation);
          const selectedImage = selectedVariation.image;

          const swiperSlides = filterProductImg.querySelectorAll('.swiper-slide');
          let targetIndex = -1;

          swiperSlides.forEach((slide, index) => {
            const imgSrc = slide.querySelector('img').getAttribute('src');
            if (imgSrc === selectedImage) {
              targetIndex = index;
              if (document.querySelector('.product-detail')) {
                targetIndex = index - 4;
              }
              if (document.querySelector('.underwear')) {
                targetIndex = index - 4;
              }
              return; // stop loop when found index
            }
          });

          if (targetIndex !== -1) {
            if (document.querySelector('.swiper-img-scroll')) swiperScrollImg.slideTo(targetIndex); // scroll slide to index
            if (document.querySelector('.underwear .mySwiper2')) swiper2.slideTo(targetIndex); // scroll slide to index
            if (document.querySelector('.product-detail .mySwiper2')) swiper2.slideTo(targetIndex); // scroll slide to index
          } else {
            console.log('Can not find Image :', selectedImage);
          }
        });
      });
    })
    .catch(error => console.error('Error fetching products:', error));
}


// Change product img when active color in list color
const handleActiveImgWhenColorChange = (products) => {
  const listColors = document.querySelectorAll(".list-color");

  listColors.forEach((list) => {
    const colorItems = list.querySelectorAll(".color-item");

    colorItems.forEach((color) => {
      color.addEventListener("click", () => {
        const activeColor = color.querySelector(".tag-action")?.textContent;
        const productMain = color.closest(".product-main");
        const dataItem = productMain?.getAttribute("data-item");
        const product = products.find((item) => item.id === dataItem);
        const imgActive = product?.variation.find(
          (item) => item.color === activeColor
        ).image;
        if (imgActive) {
          productMain.querySelector(".product-img img").remove();
          productMain.querySelector(".product-img").innerHTML = `
                            <img src="${imgActive}" alt="img" class="w-full h-full object-cover duration-700" />
                        `;
        }
      });
    });
  });
};

// Append child
const listFourProduct = document.querySelectorAll(".list-product.four-product");
const listSixProduct = document.querySelector(
  ".list-product.six-product .swiper .swiper-wrapper"
);
const listEightProduct = document.querySelector(".list-product.eight-product");
const listThreeProduct = document.querySelectorAll(
  ".list-product.three-product"
);

// Fetch products from JSON file (assuming products.json)
fetch("./assets/data/Product.json")
  .then((response) => response.json())
  .then((products) => {
    // Display the first 4 products
    if (listFourProduct) {
      listFourProduct.forEach((list) => {
        const parent = list.parentElement;
        if (parent.querySelector(".menu-tab .active")) {
          const menuItemActive = parent
            .querySelector(".menu-tab .active")
            .getAttribute("data-item");
          const menuItems = parent.querySelectorAll(".menu-tab .tab-item");

          products
            .filter((product) => product.type === menuItemActive)
            .slice(0, 4)
            .forEach((product) => {
              const productElement = createProductItem(product);
              list.appendChild(productElement);
            });

          if (list.getAttribute("data-type") === "underwear") {
            if (menuItemActive === "best sellers") {
              products
                .filter(
                  (product) =>
                    product.type === "underwear" || product.type === "swimwear"
                )
                .sort((a, b) => b.sold - a.sold)
                .slice(0, 4)
                .forEach((product) => {
                  const productElement = createProductItem(product);
                  list.appendChild(productElement);
                });
            }
          }

          menuItems.forEach((item) => {
            item.addEventListener("click", () => {
              // remove old product
              const productItems = list.querySelectorAll(".product-item");
              productItems.forEach((prdItem) => {
                prdItem.remove();
              });

              if (list.getAttribute("data-type") === "underwear") {
                if (item.getAttribute("data-item") === "best sellers") {
                  products
                    .filter(
                      (product) =>
                        product.type === "underwear" ||
                        product.type === "swimwear"
                    )
                    .sort((a, b) => b.sold - a.sold)
                    .slice(0, 4)
                    .forEach((product) => {
                      const productElement = createProductItem(product);
                      list.appendChild(productElement);
                    });
                }

                if (item.getAttribute("data-item") === "on sale") {
                  products
                    .filter(
                      (product) =>
                        product.sale &&
                        (product.type === "underwear" ||
                          product.type === "swimwear")
                    )
                    .slice(0, 4)
                    .forEach((product) => {
                      const productElement = createProductItem(product);
                      list.appendChild(productElement);
                    });
                }

                if (item.getAttribute("data-item") === "new arrivals") {
                  products
                    .filter(
                      (product) =>
                        product.new &&
                        (product.type === "underwear" ||
                          product.type === "swimwear")
                    )
                    .slice(0, 4)
                    .forEach((product) => {
                      const productElement = createProductItem(product);
                      list.appendChild(productElement);
                    });
                }
              } else {
                products
                  .filter(
                    (product) => product.type === item.getAttribute("data-item")
                  )
                  .slice(0, 4)
                  .forEach((product) => {
                    // create product
                    const productElement = createProductItem(product);
                    list.appendChild(productElement);
                  });
              }

              handleActiveImgWhenColorChange(products);
              addEventToProductItem(products);
            });
          });
        } else {
          products.slice(0, 4).forEach((product) => {
            const productElement = createProductItem(product);
            list.appendChild(productElement);
          });
        }
      });
    }

    // Display the first 6 products
    if (listSixProduct) {
      const parent = listSixProduct.parentElement.parentElement.parentElement;
      if (parent.querySelector(".menu-tab .active")) {
        const menuItemActive = parent
          .querySelector(".menu-tab .active")
          .getAttribute("data-item");
        const menuItems = parent.querySelectorAll(".menu-tab .tab-item");

        if (menuItemActive === "best sellers") {
          if (listSixProduct.getAttribute("data-type")) {
            products
              .filter(
                (product) =>
                  product.category === listSixProduct.getAttribute("data-type")
              )
              .sort((a, b) => b.sold - a.sold)
              .slice(0, 6)
              .forEach((product) => {
                const swiperSlide = document.createElement("div");
                swiperSlide.classList.add("swiper-slide");
                swiperSlide.appendChild(createProductItem(product));
                listSixProduct.appendChild(swiperSlide);
              });
          } else {
            products
              .filter((product) => product.category === "fashion")
              .sort((a, b) => b.sold - a.sold)
              .slice(0, 6)
              .forEach((product) => {
                const swiperSlide = document.createElement("div");
                swiperSlide.classList.add("swiper-slide");
                swiperSlide.appendChild(createProductItem(product));
                listSixProduct.appendChild(swiperSlide);
              });
          }
        }

        menuItems.forEach((item) => {
          item.addEventListener("click", () => {
            const productItems =
              listSixProduct.querySelectorAll(".swiper-slide");

            if (listSixProduct.getAttribute("data-type")) {
              if (item.getAttribute("data-item") === "best sellers") {
                products
                  .filter(
                    (product) =>
                      product.category ===
                      listSixProduct.getAttribute("data-type")
                  )
                  .sort((a, b) => b.sold - a.sold)
                  .slice(0, 6)
                  .forEach((product) => {
                    const swiperSlide = document.createElement("div");
                    swiperSlide.classList.add("swiper-slide");
                    swiperSlide.appendChild(createProductItem(product));
                    listSixProduct.appendChild(swiperSlide);
                  });
              }
              if (item.getAttribute("data-item") === "on sale") {
                products
                  .filter(
                    (product) =>
                      product.sale &&
                      product.category ===
                      listSixProduct.getAttribute("data-type")
                  )
                  .slice(0, 6)
                  .forEach((product) => {
                    const swiperSlide = document.createElement("div");
                    swiperSlide.classList.add("swiper-slide");
                    swiperSlide.appendChild(createProductItem(product));
                    listSixProduct.appendChild(swiperSlide);
                  });
              }
              if (item.getAttribute("data-item") === "new arrivals") {
                products
                  .filter(
                    (product) =>
                      product.new &&
                      product.category ===
                      listSixProduct.getAttribute("data-type")
                  )
                  .slice(0, 6)
                  .forEach((product) => {
                    const swiperSlide = document.createElement("div");
                    swiperSlide.classList.add("swiper-slide");
                    swiperSlide.appendChild(createProductItem(product));
                    listSixProduct.appendChild(swiperSlide);
                  });
              }
            } else {
              if (item.getAttribute("data-item") === "best sellers") {
                products
                  .filter((product) => product.category === "fashion")
                  .sort((a, b) => b.sold - a.sold)
                  .slice(0, 6)
                  .forEach((product) => {
                    const swiperSlide = document.createElement("div");
                    swiperSlide.classList.add("swiper-slide");
                    swiperSlide.appendChild(createProductItem(product));
                    listSixProduct.appendChild(swiperSlide);
                  });
              }
              if (item.getAttribute("data-item") === "on sale") {
                products
                  .filter(
                    (product) => product.sale && product.category === "fashion"
                  )
                  .slice(0, 6)
                  .forEach((product) => {
                    const swiperSlide = document.createElement("div");
                    swiperSlide.classList.add("swiper-slide");
                    swiperSlide.appendChild(createProductItem(product));
                    listSixProduct.appendChild(swiperSlide);
                  });
              }
              if (item.getAttribute("data-item") === "new arrivals") {
                products
                  .filter(
                    (product) => product.new && product.category === "fashion"
                  )
                  .slice(0, 6)
                  .forEach((product) => {
                    const swiperSlide = document.createElement("div");
                    swiperSlide.classList.add("swiper-slide");
                    swiperSlide.appendChild(createProductItem(product));
                    listSixProduct.appendChild(swiperSlide);
                  });
              }
            }

            // remove old product
            productItems.forEach((prdItem) => {
              prdItem.remove();
            });

            handleActiveImgWhenColorChange(products);
            addEventToProductItem(products);
          });
        });
      } else {
        if (listSixProduct.getAttribute("data-type")) {
          products
            .filter(
              (product) =>
                product.category === listSixProduct.getAttribute("data-type")
            )
            .slice(0, 6)
            .forEach((product) => {
              const swiperSlide = document.createElement("div");
              swiperSlide.classList.add("swiper-slide");
              swiperSlide.appendChild(createProductItem(product));
              listSixProduct.appendChild(swiperSlide);
            });
        } else {
          products.slice(5, 11).forEach((product) => {
            const swiperSlide = document.createElement("div");
            swiperSlide.classList.add("swiper-slide");
            swiperSlide.appendChild(createProductItem(product));
            listSixProduct.appendChild(swiperSlide);
          });
        }
      }
    }

    // Display the first 8 products
    if (listEightProduct) {
      const parent = listEightProduct.parentElement;
      if (parent.querySelector(".menu-tab .active")) {
        const menuItemActive = parent
          .querySelector(".menu-tab .active")
          .getAttribute("data-item");
        const menuItems = parent.querySelectorAll(".menu-tab .tab-item");

        if (menuItemActive === "best sellers") {
          products
            .filter((product) => product.category === "fashion")
            .sort((a, b) => b.sold - a.sold)
            .slice(0, 8)
            .forEach((product) => {
              const productElement = createProductItem(product);
              listEightProduct.appendChild(productElement);
            });
        }
        menuItems.forEach((item) => {
          item.addEventListener("click", () => {
            // remove old product
            const productItems =
              listEightProduct.querySelectorAll(".product-item");
            productItems.forEach((prdItem) => {
              prdItem.remove();
            });

            if (item.getAttribute("data-item") === "best sellers") {
              products
                .filter((product) => product.category === "fashion")
                .sort((a, b) => b.sold - a.sold)
                .slice(0, 8)
                .forEach((product) => {
                  const productElement = createProductItem(product);
                  listEightProduct.appendChild(productElement);
                });
            }
            if (item.getAttribute("data-item") === "on sale") {
              products
                .filter(
                  (product) => product.sale && product.category === "fashion"
                )
                .slice(0, 8)
                .forEach((product) => {
                  const productElement = createProductItem(product);
                  listEightProduct.appendChild(productElement);
                });
            }
            if (item.getAttribute("data-item") === "new arrivals") {
              products
                .filter(
                  (product) => product.new && product.category === "fashion"
                )
                .slice(0, 8)
                .forEach((product) => {
                  const productElement = createProductItem(product);
                  listEightProduct.appendChild(productElement);
                });
            }

            handleActiveImgWhenColorChange(products);
            addEventToProductItem(products);
          });
        });
      } else {
        if (listEightProduct.getAttribute("data-type")) {
          products
            .filter(
              (product) =>
                product.category === listEightProduct.getAttribute("data-type")
            )
            .slice(0, 8)
            .forEach((product) => {
              const productElement = createProductItem(product);
              listEightProduct.appendChild(productElement);
            });
        } else {
          products.slice(11, 19).forEach((product) => {
            const productElement = createProductItem(product);
            listEightProduct.appendChild(productElement);
          });
        }
      }
    }

    // Display 3 products(Home 11)
    if (listThreeProduct) {
      listThreeProduct.forEach((list) => {
        const parent = list.parentElement;
        const gender = list.getAttribute("data-gender");
        const menuItemActive = parent
          .querySelector(".menu-tab .active")
          .getAttribute("data-item");
        const menuItems = parent.querySelectorAll(".menu-tab .tab-item");

        products
          .filter(
            (product) =>
              product.gender === gender && product.type === menuItemActive
          )
          .slice(0, 3)
          .forEach((product) => {
            const productElement = createProductItem(product);
            list.appendChild(productElement);
          });

        menuItems.forEach((item) => {
          item.addEventListener("click", () => {
            // remove old product
            const productItems = list.querySelectorAll(".product-item");
            productItems.forEach((prdItem) => {
              prdItem.remove();
            });

            products
              .filter(
                (product) =>
                  product.gender === gender &&
                  product.type === item.getAttribute("data-item")
              )
              .slice(0, 3)
              .forEach((product) => {
                // create product
                const productElement = createProductItem(product);
                list.appendChild(productElement);
              });

            handleActiveImgWhenColorChange(products);
            addEventToProductItem(products);
          });
        });
      });
    }

    handleActiveImgWhenColorChange(products);
    addEventToProductItem(products);
  })
  .catch((error) => console.error("Error loading products:", error));



// create product marketplace
// Create product item
const createProductItemMarketplace = (product) => {
  const productItem = document.createElement("div");
  productItem.classList.add("product-item", "style-marketplace", "p-4", "border", "border-line", "rounded-2xl");
  productItem.setAttribute("data-item", product.id);

  let productTags = "";
  if (product.sale) {
    productTags += `<div class="product-tag text-button-uppercase text-white bg-red px-3 py-0.5 inline-block rounded-full absolute top-3 left-3 z-[1]">Sale</div>`;
  }

  let arrOfStar = "";
  for (let i = 0; i < 5; i++) {
    if (product.rate) {
      if (i >= product.rate) {
        arrOfStar += '<i class="ph-fill ph-star text-sm text-secondary"></i>';
      } else {
        arrOfStar += '<i class="ph-fill ph-star text-sm text-yellow"></i>';
      }
    }
  }

  productItem.innerHTML = `
        <div class="bg-img relative w-full aspect-1/1">
                        <img src=${product.thumbImage[0]} alt="">
                        <div class="list-action flex flex-col gap-1 absolute top-0 right-0">
                            <span
                                class="add-wishlist-btn w-8 h-8 bg-white flex items-center justify-center rounded-full box-shadow-small duration-300">
                                <i class="ph ph-heart"></i>
                            </span>
                            <span
                                class="compare-btn w-8 h-8 bg-white flex items-center justify-center rounded-full box-shadow-small duration-300">
                                <i class="ph ph-repeat"></i>
                            </span>
                            <span
                                class="quick-view-btn w-8 h-8 bg-white flex items-center justify-center rounded-full box-shadow-small duration-300">
                                <i class="ph ph-eye"></i>
                            </span>
                            <span
                                class="add-cart-btn w-8 h-8 bg-white flex items-center justify-center rounded-full box-shadow-small duration-300">
                                <i class="ph ph-shopping-bag-open"></i>
                            </span>
                        </div>
                    </div>
                    <div class="product-infor mt-4">
                        <span class="text-title">${product.name}</span>
                        <div class="flex gap-0.5 mt-1">
                            ${arrOfStar}
                        </div>
                        <span class="text-title inline-block mt-1">$${product.price}.00</span>
                    </div>
    `;

  return productItem;
};

// fetch product in marketplace
if (document.querySelector('.tab-features-block.style-marketplace')) {
  fetch("./assets/data/Product.json")
    .then((response) => response.json())
    .then((products) => {
      // Display the first 4 products
      const listProduct = document.querySelector('.tab-features-block.style-marketplace .list-product')

      if (listProduct) {
        const parent = listProduct.parentElement;
        if (parent.querySelector(".menu-tab .active")) {
          const menuItemActive = parent
            .querySelector(".menu-tab .active")
            .getAttribute("data-item");
          const menuItems = parent.querySelectorAll(".menu-tab .tab-item");

          products
            .filter((product) => product.category === menuItemActive)
            .slice(0, 5)
            .forEach((product) => {
              const productElement = createProductItemMarketplace(product);
              listProduct.appendChild(productElement);
            });

          menuItems.forEach((item) => {
            item.addEventListener("click", () => {
              // remove old product
              const productItems = listProduct.querySelectorAll(".product-item");
              productItems.forEach((prdItem) => {
                prdItem.remove();
              });

              products
                .filter(
                  (product) => product.category === item.getAttribute("data-item")
                )
                .slice(0, 5)
                .forEach((product) => {
                  // create product
                  const productElement = createProductItemMarketplace(product);
                  listProduct.appendChild(productElement);
                });

              addEventToProductItem(products);
            });
          });
        } else {
          products.slice(0, 5).forEach((product) => {
            const productElement = createProductItemMarketplace(product);
            listProduct.appendChild(productElement);
          });
        }
      }

      addEventToProductItem(products);
    })
    .catch((error) => console.error("Error loading products:", error));
}


// Featured product underwear
const handleQuantity = () => {
  const quantityBlock = document.querySelectorAll(".quantity-block");

  quantityBlock.forEach((item) => {
    const minus = item.querySelector(".ph-minus");
    const plus = item.querySelector(".ph-plus");
    const quantity = item.querySelector(".quantity");

    if (Number(quantity.textContent) < 2) {
      minus.classList.add("disabled");
    }

    minus.addEventListener("click", (e) => {
      e.stopPropagation()
      if (Number(quantity.textContent) > 2) {
        quantity.innerHTML = Number(quantity.innerHTML) - 1;
        minus.classList.remove("disabled");
      } else {
        quantity.innerHTML = "1";
        minus.classList.add("disabled");
      }
    });

    plus.addEventListener("click", (e) => {
      e.stopPropagation()
      quantity.innerHTML = Number(quantity.innerHTML) + 1;
      if (Number(quantity.textContent) >= 2) {
        minus.classList.remove("disabled");
      }
    });
  });
};

handleQuantity();

const blogItems = document.querySelectorAll(".blog-item");

blogItems.forEach((blog) => {
  // redirect to detail
  blog.addEventListener("click", () => {
    const blogId = blog.getAttribute("data-item");
    window.location.href = `blog-detail1.html?id=${blogId}`;
  });
});

// list-testimonial
if (document.querySelector(".swiper-list-testimonial")) {
  var swiperListTestimonial = new Swiper(".swiper-list-testimonial", {
    pagination: { clickable: true, el: ".swiper-pagination" },
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    touchEventsTarget: "wrapper",
    slidesPerView: 1,
    spaceBetween: 0,
    breakpoints: {
      640: {
        slidesPerView: 2,
        spaceBetween: 16,
      },
      768: {
        slidesPerView: 2,
        spaceBetween: 16,
      },
      1280: {
        slidesPerView: 3,
        spaceBetween: 30,
      },
    },
  });
}

const handleSlideActive = () => {
  let activeItem = document.querySelector(
    ".list-testimonial .swiper .swiper-slide-active"
  );
  if (activeItem) {
    const dataItem = activeItem.getAttribute("data-item");

    const listAvatar = document.querySelector(".list-avatar");
    const avatars = document.querySelectorAll(".list-avatar .bg-img");

    avatars.forEach((item) => {
      if (item.getAttribute("data-item") === dataItem) {
        if (listAvatar.querySelector(".active")) {
          listAvatar.querySelector(".active").classList.remove("active");
        }
        item.classList.add("active");
      }
    });
  }
};

handleSlideActive();

// list-testimonial 4
var swiperListTestimonialFour = new Swiper(".swiper-testimonial-four", {
  navigation: {
    prevEl: ".swiper-button-prev",
    nextEl: ".swiper-button-next",
  },
  autoplay: {
    delay: 3000,
  },
  loop: true,
  slidesPerView: 1,
  spaceBetween: 0,
  on: {
    slideChange: () => {
      handleSlideActive();
    },
  },
});

// list-testimonial yoga
if (document.querySelector(".list-testimonial-yoga")) {
  $(".list-testimonial-yoga").slick({
    dots: false,
    arrows: false,
    infinite: true,
    centerMode: true,
    centerPadding: "220px",
    speed: 300,
    autoplay: true,
    autoplaySpeed: 5000,
    slidesToShow: 3,
    slidesToScroll: 3,
    touchThreshold: 100,
    swipe: true,
    swipeToSlide: true,
    draggable: true,
    useTransform: false,
    responsive: [
      {
        breakpoint: 1600,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 3,
          centerPadding: "120px",
        },
      },
      {
        breakpoint: 1400,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 2,
          centerPadding: "160px",
        },
      },
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
          centerPadding: "160px",
        },
      },
      {
        breakpoint: 640,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
          centerPadding: "16px",
        },
      },
    ],
  });
}

// list-instagram
var swiperListInstagram = new Swiper(".swiper-list-instagram", {
  pagination: { clickable: true, el: ".swiper-pagination" },
  loop: true,
  autoplay: {
    delay: 4000,
    disableOnInteraction: false,
  },
  slidesPerView: 2,
  spaceBetween: 12,
  breakpoints: {
    640: {
      slidesPerView: 3,
      spaceBetween: 12,
    },
    768: {
      slidesPerView: 3,
      spaceBetween: 16,
    },
    1024: {
      slidesPerView: 4,
      spaceBetween: 16,
    },
    1280: {
      slidesPerView: 5,
      spaceBetween: 16,
    },
  },
});

// list-instagram 3
var swiperListInstagram = new Swiper(".swiper-instagram-three", {
  loop: true,
  autoplay: {
    delay: 4000,
    disableOnInteraction: false,
  },
  clickable: true,
  slidesPerView: 2,
  spaceBetween: 0,
  breakpoints: {
    640: {
      slidesPerView: 3,
    },
    768: {
      slidesPerView: 4,
    },
    1024: {
      slidesPerView: 5,
    },
    1280: {
      slidesPerView: 6,
    },
  },
});

// list-brand
var swiperListBrand = new Swiper(".swiper-list-brand", {
  pagination: { clickable: true, el: ".swiper-pagination" },
  loop: true,
  autoplay: {
    delay: 4000,
    disableOnInteraction: false,
  },
  slidesPerView: 2,
  spaceBetween: 12,
  breakpoints: {
    640: {
      slidesPerView: 3,
      spaceBetween: 12,
    },
    768: {
      slidesPerView: 4,
      spaceBetween: 16,
    },
    1024: {
      slidesPerView: 5,
      spaceBetween: 16,
    },
    1280: {
      slidesPerView: 6,
      spaceBetween: 16,
    },
  },
});

// list-five-brand
var swiperListBrand = new Swiper(".swiper-list-five-brand", {
  pagination: { clickable: true, el: ".swiper-pagination" },
  loop: true,
  autoplay: {
    delay: 4000,
    disableOnInteraction: false,
  },
  slidesPerView: 2,
  spaceBetween: 12,
  breakpoints: {
    640: {
      slidesPerView: 3,
      spaceBetween: 12,
    },
    768: {
      slidesPerView: 3,
      spaceBetween: 16,
    },
    1024: {
      slidesPerView: 4,
      spaceBetween: 16,
    },
    1280: {
      slidesPerView: 5,
      spaceBetween: 16,
    },
  },
});


// Before After Cosmetic1
const imageComparisonSlider = document.querySelector('[data-component="image-comparison-slider"]')

function setSliderstate(e, element) {
  const sliderRange = element.querySelector('[data-image-comparison-range]');

  if (e.type === 'input') {
    sliderRange.classList.add('image-comparison__range--active');
    return;
  }

  sliderRange.classList.remove('image-comparison__range--active');
  element.removeEventListener('mousemove', moveSliderThumb);
}

function moveSliderThumb(e) {
  const sliderRange = document.querySelector('[data-image-comparison-range]');
  const thumb = document.querySelector('[data-image-comparison-thumb]');
  let position = e.layerY - 20;

  if (e.layerY <= sliderRange.offsetTop) {
    position = -20;
  }

  if (e.layerY >= sliderRange.offsetHeight) {
    position = sliderRange.offsetHeight - 20;
  }

  thumb.style.top = `${position}px`;
}

function moveSliderRange(e, element) {
  const value = e.target.value;
  const slider = element.querySelector('[data-image-comparison-slider]');
  const imageWrapperOverlay = element.querySelector('[data-image-comparison-overlay]');

  slider.style.left = `${value}%`;
  imageWrapperOverlay.style.width = `${value}%`;

  element.addEventListener('mousemove', moveSliderThumb);
  setSliderstate(e, element);
}

function init(element) {
  const sliderRange = element.querySelector('[data-image-comparison-range]');

  if (sliderRange) {
    if ('ontouchstart' in window === false) {
      sliderRange.addEventListener('mouseup', e => setSliderstate(e, element));
      sliderRange.addEventListener('mousedown', moveSliderThumb);
    }

    sliderRange.addEventListener('input', e => moveSliderRange(e, element));
    sliderRange.addEventListener('change', e => moveSliderRange(e, element));
  }
}

if (imageComparisonSlider) {
  init(imageComparisonSlider);
}


// Change active video cosmetic2
const listCategory = document.querySelector(".list-category");
const categoryItems = document.querySelectorAll(".list-category .item");
const listItem = document.querySelector(".list-filter");
const filterItems = document.querySelectorAll(".list-filter .item");

if (categoryItems) {
  categoryItems.forEach((category) => {
    category.addEventListener("click", () => {
      filterItems.forEach((item) => {
        if (
          item.getAttribute("data-item") === category.getAttribute("data-item")
        ) {
          listCategory.querySelector(".active").classList.remove("active");
          category.classList.add("active");
          listItem.querySelector(".active").classList.remove("active");
          item.classList.add("active");
        }
      });
    });
  });
}

// Modal Video
const playIcons = document.querySelectorAll(".btn-play");
const modalVideo = document.querySelector(".modal-video-block");
const modalVideoMain = document.querySelector(
  ".modal-video-block .modal-video-main"
);

if (playIcons && modalVideo) {
  playIcons.forEach((playIcon) => {
    playIcon.addEventListener("click", () => {
      modalVideoMain.classList.add("open");
    });
  });

  modalVideo.addEventListener("click", () => {
    modalVideoMain.classList.remove("open");
  });

  modalVideoMain.addEventListener("click", (e) => {
    e.stopPropagation();
  });
}

// Scroll to top
const scrollTopBtn = document.querySelector(".scroll-to-top-btn");

window.addEventListener("scroll", () => {
  if (window.scrollY > 600) {
    scrollTopBtn.classList.add("active");
  } else {
    scrollTopBtn.classList.remove("active");
  }
});

// Handle layout cols in list product wishlist page, shop
const layoutProductList = document.querySelector(
  ".list-product-block .list-product"
);
const chooseLayoutItems = document.querySelectorAll(".choose-layout .item");

if (layoutProductList && chooseLayoutItems) {
  chooseLayoutItems.forEach((item) => {
    if (item.classList.contains("active")) {
      if (item.classList.contains("three-col")) {
        layoutProductList.classList.add("lg:grid-cols-3");
        layoutProductList.classList.remove("lg:grid-cols-4");
        layoutProductList.classList.remove("lg:grid-cols-5");
      } else if (item.classList.contains("four-col")) {
        layoutProductList.classList.add("lg:grid-cols-4");
        layoutProductList.classList.remove("lg:grid-cols-3");
        layoutProductList.classList.remove("lg:grid-cols-5");
      } else if (item.classList.contains("five-col")) {
        layoutProductList.classList.add("lg:grid-cols-5");
        layoutProductList.classList.remove("lg:grid-cols-3");
        layoutProductList.classList.remove("lg:grid-cols-4");
      }
    }

    item.addEventListener("click", () => {
      if (item.classList.contains("three-col")) {
        layoutProductList.classList.add("lg:grid-cols-3");
        layoutProductList.classList.remove("lg:grid-cols-4");
        layoutProductList.classList.remove("lg:grid-cols-5");
      } else if (item.classList.contains("four-col")) {
        layoutProductList.classList.add("lg:grid-cols-4");
        layoutProductList.classList.remove("lg:grid-cols-3");
        layoutProductList.classList.remove("lg:grid-cols-5");
      } else if (item.classList.contains("five-col")) {
        layoutProductList.classList.add("lg:grid-cols-5");
        layoutProductList.classList.remove("lg:grid-cols-3");
        layoutProductList.classList.remove("lg:grid-cols-4");
      }
    });
  });
}

// Display wishlist, cart, compare item from localStorage
const listProductWishlist = document.querySelector(
  ".wishlist-block .list-product"
);
const cartPage = document.querySelector(".cart-block");
const checkoutPage = document.querySelector(".checkout-block");
const listProductCheckout = document.querySelector(
  ".checkout-block .list-product-checkout"
);
const listProductCompare = document.querySelector(
  ".compare-block .content-main"
);

// Wishlist
if (listProductWishlist) {
  let wishlistStore = localStorage.getItem("wishlistStore");
  wishlistStore = wishlistStore ? JSON.parse(wishlistStore) : [];

  wishlistStore.forEach((product) => {
    const productElement = createProductItem(product);
    listProductWishlist.appendChild(productElement);
  });
}

// Compare page
if (listProductCompare) {
  let compareStore = localStorage.getItem("compareStore");
  compareStore = compareStore ? JSON.parse(compareStore) : [];

  const listImg = listProductCompare.querySelector(".list-product .right");
  const listRate = listProductCompare.querySelector(".list-rate-block");
  const listPrice = listProductCompare.querySelector(".list-price-block");
  const listType = listProductCompare.querySelector(".list-type-block");
  const listBrand = listProductCompare.querySelector(".list-brand-block");
  const listSize = listProductCompare.querySelector(".list-size-block");
  const listColor = listProductCompare.querySelector(".list-color-block");

  if (compareStore.length === 0) {
    listProductCompare.innerHTML = `
        <div class="flex items-center justify-between w-full">
        <div>
        <div class="text-title">No product in compare</div>
        </div>
        </div>
        `;
  } else {
    compareStore.forEach((product) => {
      // list img
      const productElement = document.createElement("div");
      productElement.setAttribute("data-item", product.id);
      productElement.classList.add(
        "product-item",
        "px-10",
        "pt-6",
        "pb-5",
        "border-r",
        "border-line",
        "cursor-pointer"
      );
      productElement.innerHTML = `
                <div class="bg-img w-full aspect-[3/4] rounded-lg overflow-hidden flex-shrink-0">
                    <img src=${product.thumbImage[0]} alt='img' class='w-full h-full object-cover' />
                </div>
                <div class="text-title text-center mt-4">${product.name}</div>
                <div class="caption2 font-semibold text-secondary2 uppercase text-center mt-1">
                    ${product.brand}
                </div>
                `;

      listImg.appendChild(productElement);

      // list star
      let arrOfStar = "";
      const rateElement = document.createElement("td");
      rateElement.classList.add(
        "w-full",
        "border",
        "border-line",
        "h-[60px]",
        "border-t-0",
        "border-r-0"
      );
      for (let i = 0; i < 5; i++) {
        if (product.rate) {
          if (i >= product.rate) {
            arrOfStar +=
              '<i class="ph-fill ph-star text-sm text-secondary"></i>';
          } else {
            arrOfStar += '<i class="ph-fill ph-star text-sm text-yellow"></i>';
          }
        }
      }

      rateElement.innerHTML = `
                <div class='h-full flex items-center justify-center'>
                    <div class="rate flex">
                        ${arrOfStar}
                    </div>
                    <p class='pl-1'>(1.234)</p>
                </div>
            `;

      listRate.appendChild(rateElement);

      // list price
      const priceElement = document.createElement("td");
      priceElement.classList.add(
        "w-full",
        "border",
        "border-line",
        "h-[60px]",
        "border-t-0",
        "border-r-0"
      );
      priceElement.innerHTML = `
                <div class='price-item h-full flex items-center justify-center'>
                    $${product.price}.00
                </div>
            `;

      listPrice.appendChild(priceElement);

      // list type
      const typeElement = document.createElement("td");
      typeElement.classList.add(
        "w-full",
        "border",
        "border-line",
        "h-[60px]",
        "border-t-0",
        "border-r-0"
      );
      typeElement.innerHTML = `
                <div class='type-item h-full flex items-center justify-center capitalize'>
                    ${product.type}
                </div>
            `;

      listType.appendChild(typeElement);

      // list brand
      const brandElement = document.createElement("td");
      brandElement.classList.add(
        "w-full",
        "border",
        "border-line",
        "h-[60px]",
        "border-t-0",
        "border-r-0"
      );
      brandElement.innerHTML = `
                <div class='brand-item h-full flex items-center justify-center capitalize'>
                    ${product.brand}
                </div>
            `;

      listBrand.appendChild(brandElement);

      // list size
      const sizeElement = document.createElement("td");
      sizeElement.classList.add(
        "w-full",
        "border",
        "border-line",
        "h-[60px]",
        "border-t-0",
        "border-r-0"
      );
      let size = "";

      if (product.sizes) {
        product.sizes.forEach((item, index) => {
          // if last size, don't add ',' in the end
          if (index === product.sizes.length - 1) {
            size += `<p>${item}</p>`;
          } else {
            size += `<p>${item}, </p>`;
          }
        });
      }

      sizeElement.innerHTML = `
                <div class='list-size h-full flex items-center justify-center capitalize gap-1'>
                    ${size}
                </div>
            `;

      listSize.appendChild(sizeElement);

      // list color
      const colorElement = document.createElement("td");
      colorElement.classList.add(
        "w-full",
        "border",
        "border-line",
        "h-[60px]",
        "border-t-0",
        "border-r-0"
      );
      let color = "";

      if (product.variation) {
        product.variation.forEach((item) => {
          color += `<span class='w-6 h-6 rounded-full' style="background-color: ${item.colorCode};"></span>`;
        });
      }

      colorElement.innerHTML = `
                <div class='list-color h-full flex items-center justify-center capitalize gap-2'>
                    ${color}
                </div>
            `;

      listColor.appendChild(colorElement);
    });
  }
}

// Cart
let listProductCart = document.querySelector(".cart-block .list-product-main");



handleInforCart();



// Show, hide login block in checkout
const formLoginHeading = document.querySelector(
  ".checkout-block .form-login-block"
);
const loginHeading = document.querySelector(
  ".checkout-block .login .left span.text-button"
);
const iconDownHeading = document.querySelector(
  ".checkout-block .login .right i"
);

if (loginHeading) {
  loginHeading.addEventListener("click", () => {
    formLoginHeading.classList.toggle("open");
    iconDownHeading.classList.toggle("up");
  });

  iconDownHeading.addEventListener("click", () => {
    formLoginHeading.classList.toggle("open");
    iconDownHeading.classList.toggle("up");
  });
}

// Show, hide payment type in checkout
const listPayment = document.querySelector(".payment-block .list-payment");
const paymentCheckbox = document.querySelectorAll(
  ".payment-block .list-payment .type>input"
);

if (paymentCheckbox) {
  paymentCheckbox.forEach((item) => {
    item.addEventListener("click", () => {
      if (listPayment.querySelector(".open")) {
        listPayment.querySelector(".open").classList.remove("open");
      }

      let parentType = item.parentElement;
      if (item.checked) {
        parentType.classList.add("open");
      }
    });
  });
}

// faqs
const menuTab = document.querySelector(".menu-tab");
const listQuestion = document.querySelector(".list-question");
const tabQuestions = document.querySelectorAll(".tab-question");
const questionItems = document.querySelectorAll(".question-item");

if (tabItems) {
  tabItems.forEach((tabItem) => {
    tabQuestions.forEach((tabQuestion) => {
      let activeMenuTab = menuTab.querySelector(".active");

      if (
        activeMenuTab.getAttribute("data-item") ===
        tabQuestion.getAttribute("data-item")
      ) {
        tabQuestion.classList.add("active");
      }

      tabItem.addEventListener("click", () => {
        if (
          tabItem.getAttribute("data-item") ===
          tabQuestion.getAttribute("data-item")
        ) {
          listQuestion.querySelector(".active").classList.remove("active");
          tabQuestion.classList.add("active");
        }
      });
    });
  });
}

if (questionItems) {
  questionItems.forEach((item, index) => {
    item.addEventListener("click", () => {
      item.classList.toggle("open");

      removeOpen(index);
    });
  });
}

function removeOpen(index1) {
  questionItems.forEach((item2, index2) => {
    if (index1 != index2) {
      item2.classList.remove("open");
    }
  });
}