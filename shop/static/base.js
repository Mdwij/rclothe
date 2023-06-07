const navBar = document.getElementById('my-navbar');
let prevScrollPos = window.pageYOffset;
window.onscroll = () => {
    let currentScrollPos = window.pageYOffset;
    if(prevScrollPos < currentScrollPos) {
        navBar.style.top = `-${navBar.offsetHeight}px`;
    } else {
        navBar.style.top = `0px`;
    }
    prevScrollPos = currentScrollPos;
}
