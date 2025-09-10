<script>
  import '../app.css';
</script>

<slot />

<div class="app">
  <slot></slot>
</div>

 <style>
  .app {
    display: contents;
    height: 100vh;
    width: 100vw;
  }
</style>
