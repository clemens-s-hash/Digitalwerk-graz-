class CountdownTimer extends HTMLElement {
    constructor() {
        super(), this.duration = parseInt(this.dataset.duration), this.initTimer(), this.updateTimer(), "true" === this.dataset.autoPlay && this.playTimer()
    }
    initTimer() {
        this.innerHTML = "", this.minutesSpan = document.createElement("span");
        let t = document.createTextNode(":");
        this.secondsSpan = document.createElement("span"), this.append(this.minutesSpan, t, this.secondsSpan)
    }
    updateTimer() {
        let t = parseInt(this.dataset.duration);
        0 === t && (t = 90);
        let e = Math.floor(t / 60),
            i = t % 60;
        this.minutesSpan.innerHTML = this.formatNumber(e), this.secondsSpan.innerHTML = this.formatNumber(i), this.dataset.duration = t - 1
    }
    playTimer() {
        this.isPlaying || (this.isPlaying = !0, this.playInterval = setInterval(() => {
            this.updateTimer()
        }, 1e3))
    }
    pauseTimer() {
        clearTimeout(this.playInterval), this.isPlaying = !0
    }
    formatNumber(t) {
        return 1 === t.toString().length ? "0" + t : t
    }
}
customElements.define("countdown-timer", CountdownTimer);