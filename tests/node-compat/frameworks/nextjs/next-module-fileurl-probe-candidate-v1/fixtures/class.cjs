module.exports = class FileUrlProbeClass {
  constructor(value) { this.value = value; }
  describe() { return 'class:' + this.value; }
};
