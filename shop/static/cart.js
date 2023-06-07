var Size
var Color
$('.display-size').click(function(){
Size = this.innerHTML;
$('.display-size').css("border","1px solid #aaaaaa");
$(this).css("border","1px solid #8b3c2f");
});
$('.display-color').click(function(){
Color = this.innerHTML;
$('.display-color').css("border","1px solid #aaaaaa");
$(this).css("border","1px solid #8b3c2f");
});

var updateBtn = document.getElementsByClassName('update-cart');
updateBtn[0].addEventListener('click',function(){
   var productId = this.dataset.product
   var action = this.dataset.action

   {% if user.is_authenticated %}
    updateUserOrder(productId,action)
   {% else %}
    window.location = "/shop/login";
   {% endif %}
});

function updateUserOrder(productId,action){
  var url = '/shop/update_cart/';

  fetch(url,{
     method:'POST',
     headers:{
       'Content-Type':'application/json',
       'X-CSRFToken':csrftoken,
     },
     body:JSON.stringify({'productId':productId,'action':action,'size':Size,'color':Color})
  })

  .then((response) =>{
    return response.json()
})

 .then((data) =>{
    console.log('data : ', data)
    location.reload()
})
}