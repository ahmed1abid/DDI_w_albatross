const VmController = artifacts.require('VmController');

module.exports = function(deployer) {
  deployer.deploy(VmController, { gas: 6721975, gasPrice: 875000000 });
};
