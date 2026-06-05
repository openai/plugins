/**
 * Generates target-specific Swift configuration for the bundled source files.
 *
 * The selected package module must be imported in the generated targets, and
 * preview filtering is intentionally a per-run launcher setting.
 *
 * @param {{packageModule: string, previewFilters: string[] | null}} options
 * @returns {string} Swift source for package import and filter constants.
 */
export function generatedPackageConfigurationSwiftSource({
  packageModule,
  previewFilters,
}) {
  return `import ${packageModule}

let previewBrowserFilters: [String]? = ${swiftOptionalStringArray(previewFilters)}
let previewBrowserIncludedModules: [String]? = [${quotedStringLiteral(packageModule)}]
`;
}

/**
 * Generates a minimal Xcode project for the host app and reload dylib target.
 *
 * The project links the user's local Swift package plus SnapshotPreviewsCore,
 * and lives entirely in a disposable workspace rather than modifying the repo.
 *
 * @param {{targetName: string, bundleId: string, packageRelativePath: string, packageProduct: string, pluginTargetName: string, deploymentTarget: string}} options
 * @returns {string} Contents of `project.pbxproj`.
 */
export function createPackageProjectFile({
  targetName,
  bundleId,
  packageRelativePath,
  packageProduct,
  pluginTargetName,
  deploymentTarget,
}) {
  const ids = {
    project: "100000000000000000000001",
    mainGroup: "100000000000000000000002",
    productGroup: "100000000000000000000003",
    targetGroup: "100000000000000000000004",
    productRef: "100000000000000000000005",
    sourceRef: "100000000000000000000006",
    sourceBuild: "100000000000000000000007",
    snapshotBuild: "100000000000000000000008",
    packageBuild: "100000000000000000000009",
    target: "10000000000000000000000A",
    sourcesPhase: "10000000000000000000000B",
    frameworksPhase: "10000000000000000000000C",
    resourcesPhase: "10000000000000000000000D",
    projectConfigList: "10000000000000000000000E",
    targetConfigList: "10000000000000000000000F",
    projectDebug: "100000000000000000000010",
    projectRelease: "100000000000000000000011",
    targetDebug: "100000000000000000000012",
    targetRelease: "100000000000000000000013",
    localPackageRef: "100000000000000000000014",
    snapshotPackageRef: "100000000000000000000015",
    packageProductRef: "100000000000000000000016",
    snapshotProductRef: "100000000000000000000017",
    pluginProductRef: "100000000000000000000018",
    pluginSourceRef: "100000000000000000000019",
    pluginSourceBuild: "10000000000000000000001A",
    pluginSnapshotBuild: "10000000000000000000001B",
    pluginPackageBuild: "10000000000000000000001C",
    pluginTarget: "10000000000000000000001D",
    pluginSourcesPhase: "10000000000000000000001E",
    pluginFrameworksPhase: "10000000000000000000001F",
    pluginConfigList: "100000000000000000000020",
    pluginDebug: "100000000000000000000021",
    pluginRelease: "100000000000000000000022",
    entriesSourceRef: "100000000000000000000023",
    entriesHostBuild: "100000000000000000000024",
    configurationSourceRef: "100000000000000000000026",
    configurationHostBuild: "100000000000000000000027",
    configurationPluginBuild: "100000000000000000000028",
    entriesPluginBuild: "100000000000000000000029",
  };

  return `// !$*UTF8*$!
{
  archiveVersion = 1;
  classes = {
  };
  objectVersion = 77;
  objects = {

/* Begin PBXBuildFile section */
    ${ids.sourceBuild} /* FocusedPreviewApp.swift in Sources */ = {isa = PBXBuildFile; fileRef = ${ids.sourceRef} /* FocusedPreviewApp.swift */; };
    ${ids.entriesHostBuild} /* PreviewBrowserEntries.swift in Sources */ = {isa = PBXBuildFile; fileRef = ${ids.entriesSourceRef} /* PreviewBrowserEntries.swift */; };
    ${ids.configurationHostBuild} /* PreviewBrowserConfiguration.swift in Sources */ = {isa = PBXBuildFile; fileRef = ${ids.configurationSourceRef} /* PreviewBrowserConfiguration.swift */; };
    ${ids.snapshotBuild} /* SnapshotPreviewsCore in Frameworks */ = {isa = PBXBuildFile; productRef = ${ids.snapshotProductRef} /* SnapshotPreviewsCore */; };
    ${ids.packageBuild} /* ${packageProduct} in Frameworks */ = {isa = PBXBuildFile; productRef = ${ids.packageProductRef} /* ${packageProduct} */; };
    ${ids.pluginSourceBuild} /* FocusedPreviewHotReloadRuntime.swift in Sources */ = {isa = PBXBuildFile; fileRef = ${ids.pluginSourceRef} /* FocusedPreviewHotReloadRuntime.swift */; };
    ${ids.entriesPluginBuild} /* PreviewBrowserEntries.swift in Sources */ = {isa = PBXBuildFile; fileRef = ${ids.entriesSourceRef} /* PreviewBrowserEntries.swift */; };
    ${ids.configurationPluginBuild} /* PreviewBrowserConfiguration.swift in Sources */ = {isa = PBXBuildFile; fileRef = ${ids.configurationSourceRef} /* PreviewBrowserConfiguration.swift */; };
    ${ids.pluginSnapshotBuild} /* SnapshotPreviewsCore in Frameworks */ = {isa = PBXBuildFile; productRef = ${ids.snapshotProductRef} /* SnapshotPreviewsCore */; };
    ${ids.pluginPackageBuild} /* ${packageProduct} in Frameworks */ = {isa = PBXBuildFile; productRef = ${ids.packageProductRef} /* ${packageProduct} */; };
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
    ${ids.productRef} /* ${targetName}.app */ = {isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = ${targetName}.app; sourceTree = BUILT_PRODUCTS_DIR; };
    ${ids.sourceRef} /* FocusedPreviewApp.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = FocusedPreviewApp.swift; sourceTree = "<group>"; };
    ${ids.pluginProductRef} /* lib${pluginTargetName}.dylib */ = {isa = PBXFileReference; explicitFileType = "compiled.mach-o.dylib"; includeInIndex = 0; path = lib${pluginTargetName}.dylib; sourceTree = BUILT_PRODUCTS_DIR; };
    ${ids.pluginSourceRef} /* FocusedPreviewHotReloadRuntime.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = FocusedPreviewHotReloadRuntime.swift; sourceTree = "<group>"; };
    ${ids.entriesSourceRef} /* PreviewBrowserEntries.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = PreviewBrowserEntries.swift; sourceTree = "<group>"; };
    ${ids.configurationSourceRef} /* PreviewBrowserConfiguration.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = PreviewBrowserConfiguration.swift; sourceTree = "<group>"; };
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
    ${ids.frameworksPhase} /* Frameworks */ = {
      isa = PBXFrameworksBuildPhase;
      buildActionMask = 2147483647;
      files = (
        ${ids.snapshotBuild} /* SnapshotPreviewsCore in Frameworks */,
        ${ids.packageBuild} /* ${packageProduct} in Frameworks */,
      );
      runOnlyForDeploymentPostprocessing = 0;
    };
    ${ids.pluginFrameworksPhase} /* Frameworks */ = {
      isa = PBXFrameworksBuildPhase;
      buildActionMask = 2147483647;
      files = (
        ${ids.pluginSnapshotBuild} /* SnapshotPreviewsCore in Frameworks */,
        ${ids.pluginPackageBuild} /* ${packageProduct} in Frameworks */,
      );
      runOnlyForDeploymentPostprocessing = 0;
    };
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
    ${ids.mainGroup} = {
      isa = PBXGroup;
      children = (
        ${ids.targetGroup} /* ${targetName} */,
        ${ids.productGroup} /* Products */,
      );
      sourceTree = "<group>";
    };
    ${ids.productGroup} /* Products */ = {
      isa = PBXGroup;
      children = (
        ${ids.productRef} /* ${targetName}.app */,
        ${ids.pluginProductRef} /* lib${pluginTargetName}.dylib */,
      );
      name = Products;
      sourceTree = "<group>";
    };
    ${ids.targetGroup} /* ${targetName} */ = {
      isa = PBXGroup;
      children = (
        ${ids.sourceRef} /* FocusedPreviewApp.swift */,
        ${ids.pluginSourceRef} /* FocusedPreviewHotReloadRuntime.swift */,
        ${ids.entriesSourceRef} /* PreviewBrowserEntries.swift */,
        ${ids.configurationSourceRef} /* PreviewBrowserConfiguration.swift */,
      );
      path = ${targetName};
      sourceTree = "<group>";
    };
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
    ${ids.target} /* ${targetName} */ = {
      isa = PBXNativeTarget;
      buildConfigurationList = ${ids.targetConfigList} /* Build configuration list for PBXNativeTarget "${targetName}" */;
      buildPhases = (
        ${ids.sourcesPhase} /* Sources */,
        ${ids.frameworksPhase} /* Frameworks */,
        ${ids.resourcesPhase} /* Resources */,
      );
      buildRules = (
      );
      dependencies = (
      );
      name = ${targetName};
      packageProductDependencies = (
        ${ids.packageProductRef} /* ${packageProduct} */,
        ${ids.snapshotProductRef} /* SnapshotPreviewsCore */,
      );
      productName = ${targetName};
      productReference = ${ids.productRef} /* ${targetName}.app */;
      productType = "com.apple.product-type.application";
    };
    ${ids.pluginTarget} /* ${pluginTargetName} */ = {
      isa = PBXNativeTarget;
      buildConfigurationList = ${ids.pluginConfigList} /* Build configuration list for PBXNativeTarget "${pluginTargetName}" */;
      buildPhases = (
        ${ids.pluginSourcesPhase} /* Sources */,
        ${ids.pluginFrameworksPhase} /* Frameworks */,
      );
      buildRules = (
      );
      dependencies = (
      );
      name = ${pluginTargetName};
      packageProductDependencies = (
        ${ids.packageProductRef} /* ${packageProduct} */,
        ${ids.snapshotProductRef} /* SnapshotPreviewsCore */,
      );
      productName = ${pluginTargetName};
      productReference = ${ids.pluginProductRef} /* lib${pluginTargetName}.dylib */;
      productType = "com.apple.product-type.library.dynamic";
    };
/* End PBXNativeTarget section */

/* Begin PBXProject section */
    ${ids.project} /* Project object */ = {
      isa = PBXProject;
      attributes = {
        BuildIndependentTargetsInParallel = 1;
        LastSwiftUpdateCheck = 2641;
        LastUpgradeCheck = 2641;
        TargetAttributes = {
          ${ids.target} = {
            CreatedOnToolsVersion = 26.4.1;
          };
          ${ids.pluginTarget} = {
            CreatedOnToolsVersion = 26.4.1;
          };
        };
      };
      buildConfigurationList = ${ids.projectConfigList} /* Build configuration list for PBXProject "PreviewHost" */;
      developmentRegion = en;
      hasScannedForEncodings = 0;
      knownRegions = (
        en,
        Base,
      );
      mainGroup = ${ids.mainGroup};
      minimizedProjectReferenceProxies = 1;
      packageReferences = (
        ${ids.localPackageRef} /* XCLocalSwiftPackageReference "${packageRelativePath}" */,
        ${ids.snapshotPackageRef} /* XCRemoteSwiftPackageReference "SnapshotPreviews-iOS" */,
      );
      preferredProjectObjectVersion = 77;
      productRefGroup = ${ids.productGroup} /* Products */;
      projectDirPath = "";
      projectRoot = "";
      targets = (
        ${ids.target} /* ${targetName} */,
        ${ids.pluginTarget} /* ${pluginTargetName} */,
      );
    };
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
    ${ids.resourcesPhase} /* Resources */ = {
      isa = PBXResourcesBuildPhase;
      buildActionMask = 2147483647;
      files = (
      );
      runOnlyForDeploymentPostprocessing = 0;
    };
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
    ${ids.sourcesPhase} /* Sources */ = {
      isa = PBXSourcesBuildPhase;
      buildActionMask = 2147483647;
      files = (
        ${ids.sourceBuild} /* FocusedPreviewApp.swift in Sources */,
        ${ids.entriesHostBuild} /* PreviewBrowserEntries.swift in Sources */,
        ${ids.configurationHostBuild} /* PreviewBrowserConfiguration.swift in Sources */,
      );
      runOnlyForDeploymentPostprocessing = 0;
    };
    ${ids.pluginSourcesPhase} /* Sources */ = {
      isa = PBXSourcesBuildPhase;
      buildActionMask = 2147483647;
      files = (
        ${ids.pluginSourceBuild} /* FocusedPreviewHotReloadRuntime.swift in Sources */,
        ${ids.entriesPluginBuild} /* PreviewBrowserEntries.swift in Sources */,
        ${ids.configurationPluginBuild} /* PreviewBrowserConfiguration.swift in Sources */,
      );
      runOnlyForDeploymentPostprocessing = 0;
    };
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
    ${ids.projectDebug} /* Debug */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
        ALWAYS_SEARCH_USER_PATHS = NO;
        CLANG_ENABLE_MODULES = YES;
        CLANG_ENABLE_OBJC_ARC = YES;
        COPY_PHASE_STRIP = NO;
        DEBUG_INFORMATION_FORMAT = dwarf;
        ENABLE_STRICT_OBJC_MSGSEND = YES;
        ENABLE_TESTABILITY = YES;
        GCC_C_LANGUAGE_STANDARD = gnu17;
        GCC_DYNAMIC_NO_PIC = NO;
        GCC_NO_COMMON_BLOCKS = YES;
        GCC_OPTIMIZATION_LEVEL = 0;
        GCC_PREPROCESSOR_DEFINITIONS = (
          "DEBUG=1",
          "$(inherited)",
        );
        GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
        GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
        GCC_WARN_UNDECLARED_SELECTOR = YES;
        GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
        GCC_WARN_UNUSED_FUNCTION = YES;
        GCC_WARN_UNUSED_VARIABLE = YES;
        IPHONEOS_DEPLOYMENT_TARGET = ${deploymentTarget};
        MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
        MTL_FAST_MATH = YES;
        ONLY_ACTIVE_ARCH = YES;
        SDKROOT = iphoneos;
        SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;
      };
      name = Debug;
    };
    ${ids.projectRelease} /* Release */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
        ALWAYS_SEARCH_USER_PATHS = NO;
        CLANG_ENABLE_MODULES = YES;
        CLANG_ENABLE_OBJC_ARC = YES;
        COPY_PHASE_STRIP = NO;
        ENABLE_NS_ASSERTIONS = NO;
        ENABLE_STRICT_OBJC_MSGSEND = YES;
        GCC_C_LANGUAGE_STANDARD = gnu17;
        GCC_NO_COMMON_BLOCKS = YES;
        GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
        GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
        IPHONEOS_DEPLOYMENT_TARGET = ${deploymentTarget};
        MTL_FAST_MATH = YES;
        SDKROOT = iphoneos;
        SWIFT_COMPILATION_MODE = wholemodule;
        VALIDATE_PRODUCT = YES;
      };
      name = Release;
    };
    ${ids.targetDebug} /* Debug */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
        ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
        CODE_SIGN_STYLE = Automatic;
        CURRENT_PROJECT_VERSION = 1;
        DEVELOPMENT_TEAM = "";
        ENABLE_PREVIEWS = NO;
        GENERATE_INFOPLIST_FILE = YES;
        INFOPLIST_KEY_CFBundleDisplayName = "SwiftUI Preview Browser";
        INFOPLIST_KEY_LSRequiresIPhoneOS = YES;
        INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
        INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
        INFOPLIST_KEY_UILaunchScreen_Generation = YES;
        INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
        INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
        LD_RUNPATH_SEARCH_PATHS = (
          "$(inherited)",
          "@executable_path/Frameworks",
        );
        MARKETING_VERSION = 1.0;
        PRODUCT_BUNDLE_IDENTIFIER = ${bundleId};
        PRODUCT_NAME = "$(TARGET_NAME)";
        SUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
        SUPPORTS_MACCATALYST = NO;
        SWIFT_EMIT_LOC_STRINGS = YES;
        SWIFT_VERSION = 6.0;
        TARGETED_DEVICE_FAMILY = "1,2";
      };
      name = Debug;
    };
    ${ids.targetRelease} /* Release */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
        ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
        CODE_SIGN_STYLE = Automatic;
        CURRENT_PROJECT_VERSION = 1;
        DEVELOPMENT_TEAM = "";
        ENABLE_PREVIEWS = NO;
        GENERATE_INFOPLIST_FILE = YES;
        INFOPLIST_KEY_CFBundleDisplayName = "SwiftUI Preview Browser";
        INFOPLIST_KEY_LSRequiresIPhoneOS = YES;
        INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
        INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
        INFOPLIST_KEY_UILaunchScreen_Generation = YES;
        LD_RUNPATH_SEARCH_PATHS = (
          "$(inherited)",
          "@executable_path/Frameworks",
        );
        MARKETING_VERSION = 1.0;
        PRODUCT_BUNDLE_IDENTIFIER = ${bundleId};
        PRODUCT_NAME = "$(TARGET_NAME)";
        SUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
        SUPPORTS_MACCATALYST = NO;
        SWIFT_EMIT_LOC_STRINGS = YES;
        SWIFT_VERSION = 6.0;
        TARGETED_DEVICE_FAMILY = "1,2";
      };
      name = Release;
    };
    ${ids.pluginDebug} /* Debug */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
        CODE_SIGN_STYLE = Automatic;
        CURRENT_PROJECT_VERSION = 1;
        DEVELOPMENT_TEAM = "";
        EXECUTABLE_PREFIX = lib;
        MACH_O_TYPE = mh_dylib;
        MARKETING_VERSION = 1.0;
        PRODUCT_NAME = "$(TARGET_NAME)";
        SKIP_INSTALL = YES;
        SUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
        SUPPORTS_MACCATALYST = NO;
        SWIFT_EMIT_LOC_STRINGS = YES;
        SWIFT_VERSION = 6.0;
        TARGETED_DEVICE_FAMILY = "1,2";
      };
      name = Debug;
    };
    ${ids.pluginRelease} /* Release */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
        CODE_SIGN_STYLE = Automatic;
        CURRENT_PROJECT_VERSION = 1;
        DEVELOPMENT_TEAM = "";
        EXECUTABLE_PREFIX = lib;
        MACH_O_TYPE = mh_dylib;
        MARKETING_VERSION = 1.0;
        PRODUCT_NAME = "$(TARGET_NAME)";
        SKIP_INSTALL = YES;
        SUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
        SUPPORTS_MACCATALYST = NO;
        SWIFT_EMIT_LOC_STRINGS = YES;
        SWIFT_VERSION = 6.0;
        TARGETED_DEVICE_FAMILY = "1,2";
      };
      name = Release;
    };
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
    ${ids.projectConfigList} /* Build configuration list for PBXProject "PreviewHost" */ = {
      isa = XCConfigurationList;
      buildConfigurations = (
        ${ids.projectDebug} /* Debug */,
        ${ids.projectRelease} /* Release */,
      );
      defaultConfigurationIsVisible = 0;
      defaultConfigurationName = Release;
    };
    ${ids.targetConfigList} /* Build configuration list for PBXNativeTarget "${targetName}" */ = {
      isa = XCConfigurationList;
      buildConfigurations = (
        ${ids.targetDebug} /* Debug */,
        ${ids.targetRelease} /* Release */,
      );
      defaultConfigurationIsVisible = 0;
      defaultConfigurationName = Release;
    };
    ${ids.pluginConfigList} /* Build configuration list for PBXNativeTarget "${pluginTargetName}" */ = {
      isa = XCConfigurationList;
      buildConfigurations = (
        ${ids.pluginDebug} /* Debug */,
        ${ids.pluginRelease} /* Release */,
      );
      defaultConfigurationIsVisible = 0;
      defaultConfigurationName = Release;
    };
/* End XCConfigurationList section */

/* Begin XCLocalSwiftPackageReference section */
    ${ids.localPackageRef} /* XCLocalSwiftPackageReference "${packageRelativePath}" */ = {
      isa = XCLocalSwiftPackageReference;
      relativePath = ${quotedStringLiteral(packageRelativePath)};
    };
/* End XCLocalSwiftPackageReference section */

/* Begin XCRemoteSwiftPackageReference section */
    ${ids.snapshotPackageRef} /* XCRemoteSwiftPackageReference "SnapshotPreviews-iOS" */ = {
      isa = XCRemoteSwiftPackageReference;
      repositoryURL = "https://github.com/EmergeTools/SnapshotPreviews-iOS.git";
      requirement = {
        kind = revision;
        revision = d42446f0439217941a4e3a2ca58a643c1ac328c4;
      };
    };
/* End XCRemoteSwiftPackageReference section */

/* Begin XCSwiftPackageProductDependency section */
    ${ids.packageProductRef} /* ${packageProduct} */ = {
      isa = XCSwiftPackageProductDependency;
      package = ${ids.localPackageRef} /* XCLocalSwiftPackageReference "${packageRelativePath}" */;
      productName = ${quotedStringLiteral(packageProduct)};
    };
    ${ids.snapshotProductRef} /* SnapshotPreviewsCore */ = {
      isa = XCSwiftPackageProductDependency;
      package = ${ids.snapshotPackageRef} /* XCRemoteSwiftPackageReference "SnapshotPreviews-iOS" */;
      productName = SnapshotPreviewsCore;
    };
/* End XCSwiftPackageProductDependency section */
  };
  rootObject = ${ids.project} /* Project object */;
}
`;
}

/**
 * Serializes an optional list of filter strings as a Swift array literal.
 *
 * @param {string[] | null} values Preview filters, or `null` for no filtering.
 * @returns {string} Swift source for an optional string array.
 */
function swiftOptionalStringArray(values) {
  return values?.length ? `[${values.map(quotedStringLiteral).join(", ")}]` : "nil";
}

/**
 * Serializes user-derived text as a quoted Swift- and project-compatible literal.
 *
 * @param {string} value Value inserted into generated Swift or project text.
 * @returns {string} Quoted literal with required escaping.
 */
function quotedStringLiteral(value) {
  return JSON.stringify(value);
}
