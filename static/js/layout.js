  $(function (){
    /* Dynamic Serach */
  $('#nav-search').keyup(function(){
    let searchString = $(this).val().toUpperCase();
    $('.card-text').each(function(){
      if($(this).text().toUpperCase().indexOf(searchString) > -1){
        $(this).parent().parent()
          .removeClass('d-none')
      }else{
        $(this).parent().parent()
          .addClass('d-none')
      }
    });
    $('.card-title').each(function(){
    if($(this).text().toUpperCase().indexOf(searchString) > -1){
        $(this).parent()
          .removeClass('d-none')
      }else{
        $(this).parent()
          .addClass('d-none')
      }
    });
  });
    /* Fancy hover effect */
    $('.card-icon').hover(
      function(){
        $(this).removeClass('bg-info')
        $(this)
          .siblings()
          .first()
          .addClass('bg-info')
      },
      function(){
        $(this).addClass('bg-info')
        $(this)
          .siblings()
          .first()
          .removeClass('bg-info')
      }
    );
    $('.card-text').hover(
      function(){
        $(this)
          .addClass('bg-info')
          .addClass('text-white')
        $(this)
          .siblings()
          .first()
          .removeClass('bg-info')
      },
      function(){
        $(this)
          .removeClass('bg-info')
          .removeClass('text-white')
        $(this)
          .siblings()
          .first()
          .addClass('bg-info')
      }
    );
  });