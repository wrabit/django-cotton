export default () => ({
    loadSuccess: false,
    image: {
        ['x-show']() {
            return this.loadSuccess;
        },
        ['x-cloak']() {
            return true;
        },
        ['x-on:load']() {
            return this.loadSuccess = true;
        },
    },
    fallback: {
        ['x-show']() {
            return !this.loadSuccess;
        },
        ['x-cloak']() {
            return true;
        },
    }
})
