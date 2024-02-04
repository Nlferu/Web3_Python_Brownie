// An NFT Contract where the tokenURI can be one of 3 different dog's randomly selected

// SPDX-License-Identifier: MIT

pragma solidity 0.6.6;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract AdvancedCollectible is ERC721, VRFConsumerBase {
    uint256 public tokenCounter;
    bytes32 public keyHash;
    uint256 public fee;
    enum Breed{PUG, SHIBA_INU, ST_BERNARD}
    // Each time we update mapping, good practice is to Emit Events!
    mapping(uint256 => Breed) public tokenIdToBreed;
    event breedAssign(uint256 indexed newTokenId, Breed breed);
    mapping(bytes32 => address) public requestIdToSender;
    // The "indexed" keyword just makes it easier to search for this event
    // Below will be "emmited" when we call "requestIdToSender" because we are updating mapping here
    event requestedCollectible(bytes32 indexed requestId, address requester);

    constructor(address _VRFCoordinator, address _linkToken, bytes32 _keyHash, uint256 _fee) public
    VRFConsumerBase(_VRFCoordinator, _linkToken)
    ERC721("Dogie", "DOG")
    {
        tokenCounter = 0;
        keyHash = _keyHash;
        fee = _fee;
    }

    function createCollectible() public returns (bytes32) {
        bytes32 requestId = requestRandomness(keyHash, fee);
        requestIdToSender[requestId] = msg.sender;
        emit requestedCollectible(requestId, msg.sender);
    }

    // If it's internal only the VRFCoordinator can call this
    function fulfillRandomness(bytes32 requestId, uint256 randomNumber) internal override {
        // Our "breed" variable is type "Breed"
        Breed breed = Breed(randomNumber % 3);
        // We need to assign above "breed" to it's token Id (We will use mapping)
        uint256 newTokenId = tokenCounter;
        tokenIdToBreed[newTokenId] = breed;
        emit breedAssign(newTokenId, breed);
        // The "owner" is "msg.sender" but is always gonna be the "VRFCoordinator" since "VRFCoordinator" is calling function "fulfillRandomness"
        address owner = requestIdToSender[requestId];
        _safeMint(owner, newTokenId);
        // As we have now chosing breed by random number, we can delete "string memory tokenURI" parameter from "createCollectible" function and we will
        // set our token URI in separate function
        // _setTokenURI(newTokenId, tokenURI);
        tokenCounter += 1;
    }

    function setTokenURI(uint256 tokenId, string memory _tokenURI) public {
        /**
            We need 3 differens tokenURI's for each breed (pug, shiba inu, st bernard) and let only owner of token update token URI's
            to do that we are going to use imported OpenZeppelin function _isApprovedOrOwner() from ERC721
            and "_msgSender()" from https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Context.sol
        */
        require(_isApprovedOrOwner(_msgSender(), tokenId), "ERC721: caller is not token owner or approved");
        _setTokenURI(tokenId, _tokenURI);
    }
}
