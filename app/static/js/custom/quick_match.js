// $(document).ready( function() {
//
//   var new_sub;
//   var sub_count = $('.sub').length;
//
//   if (sub_count > 2) {
//     $('.add-sub').hide();
//   } else {
//     $('.add-sub').show();
//   }
//
//   $(document).on('click touchstart', '.sub .glyphicon-remove', function(e) {
//     $(this).parent().remove();
//     $('.add-sub').show();
//   });
//
//   $(document).on('click touchstart', '.add-sub', function(e) {
//     sub_count = $('.sub').length;
//
//     console.log(sub_count);
//
//     new_sub = $("<span class='badge sub'>/r/<span class='sub-name' contenteditable=true>subreddit</span> <span class='glyphicon glyphicon-remove'></span></span>");
//
//     if (sub_count < 3) {
//       $('.sub-filters').append(new_sub);
//       if (sub_count == 2) {
//         $('.add-sub').hide();
//       }
//     } else {
//       $('.add-sub').hide();
//     }
//
//   });
//
// });
