'use strict';

function openModal(){
   document.getElementById('zoom01').showModal();
}

function setNewImgPath(splitImgPath, thumbTxt){
  var begPath = splitImgPath[0];
  var endPath = splitImgPath[1];
  var newImgPath = begPath + "_1x" + endPath;
  $('#zoom01').find('.modal-photo').attr('src', newImgPath);
  $('#zoom01').find('.zoom-label').text(thumbTxt);
  openModal();
}

var smPhotoZoom = function(thumbImg, thumbTxt){
  var splitImgPath = thumbImg.split('_pt33x');
  setNewImgPath(splitImgPath, thumbTxt);
};

var mdPhotoZoom = function(thumbImg, thumbTxt){
  var splitImgPath = thumbImg.split('_pt50x');
  setNewImgPath(splitImgPath, thumbTxt);
};

$(document).ready(function() {
  $('.zoom-fig-md').click(function(){
    var thumbImg = $(this).find('.zoom-but-md').attr('src');
    var thumbTxt = $(this).find('.zoom-but-md').attr('alt');
    mdPhotoZoom(thumbImg, thumbTxt);
  });
  $('.zoom-fig-sm').click(function(){
    var thumbImg = $(this).find('.zoom-but-sm').attr('src');
    var thumbTxt = $(this).find('.zoom-but-sm').attr('alt');
    smPhotoZoom(thumbImg, thumbTxt);
  });

});

