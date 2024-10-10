module.exports = async () => {
  await new Promise(resolve => setTimeout(resolve, 500));
  if (global.gc) {
    global.gc();
  }
};
