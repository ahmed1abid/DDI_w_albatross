const DataRegistry = artifacts.require("DataRegistry");

module.exports = function(deployer) {
  deployer.deploy(DataRegistry, { gas: 6721975, gasPrice: 875000000 });
};
