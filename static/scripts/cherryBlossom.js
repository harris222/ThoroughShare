$(function(){
  $('.navbar-top').sakura({
    blowAnimations: ['blow-soft-left', 'blow-medium-left', 'blow-soft-right', 'blow-medium-right'],
    className: 'sakura',
    fallSpeed: 1, // higher is slower
    maxSize: 14,
    minSize: 10,
    newOn: 300, // Interval
    swayAnimations: ['sway-0', 'sway-1', 'sway-2', 'sway-3', 'sway-4', 'sway-5', 'sway-6', 'sway-7', 'sway-8']
  });
});
