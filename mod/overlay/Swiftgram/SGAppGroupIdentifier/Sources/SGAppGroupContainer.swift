import Foundation

// MARK: Lumigram
// When the app is re-signed with a free Apple ID (Sideloadly, AltStore) the App Group
// may be renamed or missing, and containerURL(forSecurityApplicationGroupIdentifier:)
// returns nil. Telegram keeps its whole database in that container, so without a
// fallback the app stops at launch with "Error 2". The mod ships no app extensions,
// so a private folder inside the app sandbox works just as well.

public func sgHasRealAppGroupContainer(_ appGroupName: String) -> Bool {
    return FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: appGroupName) != nil
}

public func sgAppGroupContainerURL(_ appGroupName: String) -> URL? {
    if let url = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: appGroupName) {
        return url
    }
    guard let supportUrl = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first else {
        return nil
    }
    let fallbackUrl = supportUrl.appendingPathComponent("AppGroupFallback", isDirectory: true)
    do {
        try FileManager.default.createDirectory(at: fallbackUrl, withIntermediateDirectories: true, attributes: nil)
    } catch {
        return nil
    }
    return fallbackUrl
}
