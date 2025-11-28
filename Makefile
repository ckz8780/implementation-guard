hardhat: ## Runs a local hardhat node
	npx hardhat node

compile: ## Runs npx hardhat clean/compile
	npx hardhat clean && npx hardhat compile --show-stack-traces