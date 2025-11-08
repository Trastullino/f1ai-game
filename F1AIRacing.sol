// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title F1AI Racing Registry
 * @notice Ultra-simple public registry for race entries
 * @dev Anyone can register. Anyone can read. Server processes off-chain.
 */
contract F1AIRacing {
    
    // Race entry - just encrypted car and signature
    struct RaceEntry {
        address playerAddress;
        uint256 userId;
        bytes encryptedCar;
        bytes signature;
        uint256 timestamp;
    }
    
    // All race entries (public)
    RaceEntry[] public entries;
    
    // Track if user already entered (prevent duplicates)
    mapping(uint256 => bool) public hasEntered;
    
    // Events
    event CarRegistered(
        uint256 indexed entryId,
        uint256 indexed userId,
        address indexed playerAddress,
        uint256 timestamp
    );
    
    /**
     * @notice Register a car for the race
     * @param userId Your user ID
     * @param encryptedCar Your encrypted car data
     * @param signature Ed25519 signature on the encrypted car
     */
    function registerCar(
        uint256 userId,
        bytes calldata encryptedCar,
        bytes calldata signature
    ) external {
        require(!hasEntered[userId], "User already registered");
        require(encryptedCar.length > 0, "Empty car data");
        require(signature.length == 64, "Invalid signature length (must be 64 bytes)");
        
        // Create entry
        RaceEntry memory entry = RaceEntry({
            playerAddress: msg.sender,
            userId: userId,
            encryptedCar: encryptedCar,
            signature: signature,
            timestamp: block.timestamp
        });
        
        // Store entry
        entries.push(entry);
        hasEntered[userId] = true;
        
        emit CarRegistered(entries.length - 1, userId, msg.sender, block.timestamp);
    }
    
    /**
     * @notice Get all registered entries
     * @return Array of all race entries
     */
    function getAllEntries() external view returns (RaceEntry[] memory) {
        return entries;
    }
    
    /**
     * @notice Get a specific entry by ID
     * @param entryId The entry ID (index)
     * @return The race entry
     */
    function getEntry(uint256 entryId) external view returns (RaceEntry memory) {
        require(entryId < entries.length, "Entry does not exist");
        return entries[entryId];
    }
    
    /**
     * @notice Get total number of registered entries
     * @return Total count
     */
    function getEntryCount() external view returns (uint256) {
        return entries.length;
    }
    
    /**
     * @notice Check if a user has registered
     * @param userId The user ID
     * @return True if registered
     */
    function isUserRegistered(uint256 userId) external view returns (bool) {
        return hasEntered[userId];
    }
}
