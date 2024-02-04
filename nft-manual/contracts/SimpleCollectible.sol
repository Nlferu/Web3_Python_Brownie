// SPDX-License-Identifier: MIT

pragma solidity 0.6.6;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

// We make many NFT's, but they are all contained in this one contract
contract SimpleCollectible is ERC721 {
    uint256 public tokenCounter;

    // We give it "Name" and "Symbol"
    constructor() public ERC721("Dogie", "DOG") {
        tokenCounter = 0;
    }

    // Creating new NFT is just mapping (assigning) tokenId to a new address (owner)
    function createCollectible(string memory tokenURI) public returns (uint256) {
        // Check ERC721 contract structure "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol" 
        // The difference between "_mint" and _safeMint it's "_safeMint" checks if tokenId has been already used or not
        uint256 newTokenId = tokenCounter;
        // Whenever we mint one we increase our "tokenCounter" value
        _safeMint(msg.sender, newTokenId);
        // Below function was removed from original ERC721 and can be found here:
        // https://docs.openzeppelin.com/contracts/2.x/api/token/erc721#ERC721Metadata-_setTokenURI-uint256-string-
        // or here: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721URIStorage.sol
        // It is not included in newest library version but it is included in 3.4.0v of openzeppelin here:
        // https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v3.4/contracts/token/ERC721/ERC721.sol 
        _setTokenURI(newTokenId, tokenURI);
        tokenCounter += 1;
        return newTokenId;
    }
}
