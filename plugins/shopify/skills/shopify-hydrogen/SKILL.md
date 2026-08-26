---
name: shopify-hydrogen
description: "Hydrogen storefront implementation cookbooks. Some of the available recipes are: B2B Commerce, Bundles, Combined Listings, Custom Cart Method, Dynamic Content with Metaobjects, Express Server, Google Tag Manager Integration, Infinite Scroll, Legacy Customer Account Flow, Markets, Partytown + Google Tag Manager, Subscriptions, Third-party API Queries and Caching. MANDATORY: Use this API for ANY Hydrogen storefront question - do NOT use Storefront GraphQL when 'Hydrogen' is mentioned."
compatibility: Requires Node.js
metadata:
  author: Shopify
  version: "1.9.1"
---

## Required Tool Calls (do not skip)

You have a `bash` tool. Every response must use it — in this order:

1. Call `bash` with `scripts/search_docs.mjs "<query>"` — search before writing code
2. Write the code using the search results
3. Call `bash` with `scripts/validate.mjs --code '...' --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER` — validate before returning
   (Always include these flags. Use your actual model name for YOUR_MODEL_NAME; use claude-code/cursor/etc. for YOUR_CLIENT_NAME. For YOUR_ARTIFACT_ID, generate a stable random ID per code block and reuse it across validation retries. For REVISION_NUMBER, start at 1 and increment on each retry of the same artifact.)
4. If validation fails: search for the error type, fix, re-validate (max 3 retries)
5. Return code only after validation passes

**You must run both search_docs.mjs and validate.mjs in every response. Do not return code to the user without completing step 3.**

---

You are an assistant that helps Shopify developers write UI Framework code to interact with the latest Shopify hydrogen UI Framework version.

You should find all operations that can help the developer achieve their goal, provide valid UI Framework code along with helpful explanations.
DO NOT USE HYDROGEN REACT, ONLY USE HYDROGEN.

References:

- /docs/storefronts/headless/hydrogen/cookbook

## Hydrogen Cookbook - Ready-to-Use Recipes

Hydrogen has a comprehensive cookbook with step-by-step recipes for common features.
Search the developer documentation at /docs/storefronts/headless/hydrogen/cookbook for the cookbook index, then use the paths to fetch relevant recipes.
Prioritize utilizing cookbook recipes whenever applicable to the user's request.

## 🚨 CRITICAL ERROR PREVENTION 🚨

NEVER use api:"storefront" for these components - they are REACT COMPONENTS:

- Image, Video, ExternalVideo, MediaFile, Money - NOT GraphQL types!
- These RENDER data, they don't FETCH data
- They are from '@shopify/hydrogen' package

## MANDATORY REQUIREMENTS:

1. **ALWAYS** use api:"hydrogen" for ALL components below
2. **ALWAYS** generate complete JSX code examples
3. If asked about "Media" or "MediaFile" - use api:"hydrogen" NOT api:"storefront"!

## REMEMBER:

- These components CONSUME data from Storefront API
- They are NOT the data types themselves
- They are React UI components that render HTML

## Hydrogen Component Types

Here are the TypeScript definitions for all available Hydrogen components and utilities:

```typescript
// --- @shopify/hydrogen/dist/production/index.d.ts ---
import * as react from 'react';
import { ReactNode, ComponentType, ScriptHTMLAttributes, FC, ForwardRefExoticComponent, RefAttributes, ComponentProps } from 'react';
import { BuyerInput, CountryCode as CountryCode$1, LanguageCode as LanguageCode$1, VisitorConsent as VisitorConsent$1, CartInput, CartLineInput, CartLineUpdateInput, CartBuyerIdentityInput, CartSelectedDeliveryOptionInput, AttributeInput, Scalars, CartSelectableAddressInput, CartSelectableAddressUpdateInput, Cart, CartMetafieldsSetInput, CartUserError, MetafieldsSetUserError, MetafieldDeleteUserError, CartWarning, Product, ProductVariant, CartLine, ComponentizableCartLine, CurrencyCode, PageInfo, Maybe, ProductOptionValue, ProductOption, ProductVariantConnection, SelectedOptionInput } from '@shopify/hydrogen-react/storefront-api-types';
import { createStorefrontClient as createStorefrontClient$1, StorefrontClientProps, RichText as RichText$1, ShopPayButton as ShopPayButton$1 } from '@shopify/hydrogen-react';
export { AnalyticsEventName, AnalyticsPageType, ClientBrowserParameters, ExternalVideo, IMAGE_FRAGMENT, Image, MappedProductOptions, MediaFile, ModelViewer, Money, ParsedMetafields, ShopifyAnalytics as SendShopifyAnalyticsEvent, ShopifyAddToCart, ShopifyAddToCartPayload, ShopifyAnalyticsPayload, ShopifyAnalyticsProduct, ShopifyCookies, ShopifyPageView, ShopifyPageViewPayload, ShopifySalesChannel, StorefrontApiResponse, StorefrontApiResponseError, StorefrontApiResponseOk, StorefrontApiResponseOkPartial, StorefrontApiResponsePartial, Video, customerAccountApiCustomScalars, decodeEncodedVariant, flattenConnection, getAdjacentAndFirstAvailableVariants, getClientBrowserParameters, getProductOptions, getShopifyCookies, getTrackingValues, isOptionValueCombinationInEncodedVariant, mapSelectedProductOptionToObject, parseGid, parseMetafield, sendShopifyAnalytics, storefrontApiCustomScalars, useLoadScript, useMoney, useSelectedOptionInUrlParam, useShopifyCookies } from '@shopify/hydrogen-react';
import { LanguageCode, CountryCode } from '@shopify/hydrogen-react/customer-account-api-types';
import { ExecutionArgs } from 'graphql';
import * as react_router from 'react-router';
import { SessionData, FlashSessionData, Session, SessionStorage, RouterContextProvider, FetcherWithComponents, ServerBuild, LinkProps, LoaderFunctionArgs, MetaFunction, LoaderFunction, Params, Location } from 'react-router';
import * as react_jsx_runtime from 'react/jsx-runtime';
import { PartialDeep } from 'type-fest';
import { RouteConfigEntry } from '@react-router/dev/routes';
import { Preset } from '@react-router/dev/config';
import { WithContext, Thing } from 'schema-dts';

/**
 * Override options for a cache strategy.
 */
interface AllCacheOptions {
    /**
     * The caching mode, generally `public`, `private`, or `no-store`.
     */
    mode?: string;
    /**
     * The maximum amount of time in seconds that a resource will be considered fresh. See `max-age` in the [MDN docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#:~:text=Response%20Directives-,max%2Dage,-The%20max%2Dage).
     */
    maxAge?: number;
    /**
     * Indicate that the cache should serve the stale response in the background while revalidating the cache. See `stale-while-revalidate` in the [MDN docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#stale-while-revalidate).
     */
    staleWhileRevalidate?: number;
    /**
     * Similar to `maxAge` but specific to shared caches. See `s-maxage` in the [MDN docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#s-maxage).
     */
    sMaxAge?: number;
    /**
     * Indicate that the cache should serve the stale response if an error occurs while revalidating the cache. See `stale-if-error` in the [MDN docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#stale-if-error).
     */
    staleIfError?: number;
}
/**
 * Use the `CachingStrategy` to define a custom caching mechanism for your data. Or use one of the pre-defined caching strategies: CacheNone, CacheShort, CacheLong.
 */
type CachingStrategy = AllCacheOptions;
type NoStoreStrategy = {
    mode: string;
};
declare function generateCacheControlHeader(cacheOptions: CachingStrategy): string;
/**
 *
 * @public
 */
declare function CacheNone(): NoStoreStrategy;
/**
 *
 * @public
 */
declare function CacheShort(overrideOptions?: CachingStrategy): AllCacheOptions;
/**
 *
 * @public
 */
declare function CacheLong(overrideOptions?: CachingStrategy): AllCacheOptions;
/**
 *
 * @public
 */
declare function CacheCustom(overrideOptions: CachingStrategy): AllCacheOptions;

/**
Convert a union type to an intersection type using [distributive conditional types](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-8.html#distributive-conditional-types).

Inspired by [this Stack Overflow answer](https://stackoverflow.com/a/50375286/2172153).

@example
```

import type {UnionToIntersection} from 'type-fest';

type Union = {the(): void} | {great(arg: string): void} | {escape: boolean};

type Intersection = UnionToIntersection<Union>;
//=> {the(): void; great(arg: string): void; escape: boolean};

```

A more applicable example which could make its way into your library code follows.

@example
```

import type {UnionToIntersection} from 'type-fest';

class CommandOne {
commands: {
a1: () => undefined,
b1: () => undefined,
}
}

class CommandTwo {
commands: {
a2: (argA: string) => undefined,
b2: (argB: string) => undefined,
}
}

const union = [new CommandOne(), new CommandTwo()].map(instance => instance.commands);
type Union = typeof union;
//=> {a1(): void; b1(): void} | {a2(argA: string): void; b2(argB: string): void}

type Intersection = UnionToIntersection<Union>;
//=> {a1(): void; b1(): void; a2(argA: string): void; b2(argB: string): void}

```

@category Type
*/
type UnionToIntersection<Union> = (
// `extends unknown` is always going to be the case and is used to convert the
// `Union` into a [distributive conditional
// type](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-8.html#distributive-conditional-types).
Union extends unknown ? (distributedUnion: Union) => void : never) extends ((mergedIntersection: infer Intersection) => void) ? Intersection & Union : never;
/**
Create a union of all keys from a given type, even those exclusive to specific union members.

Unlike the native `keyof` keyword, which returns keys present in **all** union members, this type returns keys from **any** member.

@link https://stackoverflow.com/a/49402091

@example
```

import type {KeysOfUnion} from 'type-fest';

type A = {
common: string;
a: number;
};

type B = {
common: string;
b: string;
};

type C = {
common: string;
c: boolean;
};

type Union = A | B | C;

type CommonKeys = keyof Union;
//=> 'common'

type AllKeys = KeysOfUnion<Union>;
//=> 'common' | 'a' | 'b' | 'c'

```

@category Object
*/
type KeysOfUnion<ObjectType> =
// Hack to fix https://github.com/sindresorhus/type-fest/issues/1008
keyof UnionToIntersection<ObjectType extends unknown ? Record<keyof ObjectType, never> : never>;
/**
Extract all optional keys from the given type.

This is useful when you want to create a new type that contains different type values for the optional keys only.

@example
```

import type {OptionalKeysOf, Except} from 'type-fest';

interface User {
name: string;
surname: string;

    luckyNumber?: number;

}

const REMOVE_FIELD = Symbol('remove field symbol');
type UpdateOperation<Entity extends object> = Except<Partial<Entity>, OptionalKeysOf<Entity>> & {
[Key in OptionalKeysOf<Entity>]?: Entity[Key] | typeof REMOVE_FIELD;
};

const update1: UpdateOperation<User> = {
name: 'Alice'
};

const update2: UpdateOperation<User> = {
name: 'Bob',
luckyNumber: REMOVE_FIELD
};

```

@category Utilities
*/
type OptionalKeysOf<BaseType extends object> = BaseType extends unknown // For distributing `BaseType`
 ? (keyof {
	[Key in keyof BaseType as BaseType extends Record<Key, BaseType[Key]> ? never : Key]: never;
}) & (keyof BaseType) // Intersect with `keyof BaseType` to ensure result of `OptionalKeysOf<BaseType>` is always assignable to `keyof BaseType`
 : never; // Should never happen
/**
Extract all required keys from the given type.

This is useful when you want to create a new type that contains different type values for the required keys only or use the list of keys for validation purposes, etc...

@example
```

import type {RequiredKeysOf} from 'type-fest';

declare function createValidation<Entity extends object, Key extends RequiredKeysOf<Entity> = RequiredKeysOf<Entity>>(field: Key, validator: (value: Entity[Key]) => boolean): ValidatorFn;

interface User {
name: string;
surname: string;

    luckyNumber?: number;

}

const validator1 = createValidation<User>('name', value => value.length < 25);
const validator2 = createValidation<User>('surname', value => value.length < 25);

```

@category Utilities
*/
type RequiredKeysOf<BaseType extends object> = BaseType extends unknown // For distributing `BaseType`
 ? Exclude<keyof BaseType, OptionalKeysOf<BaseType>> : never; // Should never happen
/**
Returns a boolean for whether the given type is `never`.

@link https://github.com/microsoft/TypeScript/issues/31751#issuecomment-498526919
@link https://stackoverflow.com/a/53984913/10292952
@link https://www.zhenghao.io/posts/ts-never

Useful in type utilities, such as checking if something does not occur.

@example
```

import type {IsNever, And} from 'type-fest';

// https://github.com/andnp/SimplyTyped/blob/master/src/types/strings.ts
type AreStringsEqual<A extends string, B extends string> =
And<
IsNever<Exclude<A, B>> extends true ? true : false,
IsNever<Exclude<B, A>> extends true ? true : false >;

type EndIfEqual<I extends string, O extends string> =
AreStringsEqual<I, O> extends true
? never
: void;

function endIfEqual<I extends string, O extends string>(input: I, output: O): EndIfEqual<I, O> {
if (input === output) {
process.exit(0);
}
}

endIfEqual('abc', 'abc');
//=> never

endIfEqual('abc', '123');
//=> void

```

@category Type Guard
@category Utilities
*/
type IsNever<T> = [
	T
] extends [
	never
] ? true : false;
/**
An if-else-like type that resolves depending on whether the given type is `never`.

@see {@link IsNever}

@example
```

import type {IfNever} from 'type-fest';

type ShouldBeTrue = IfNever<never>;
//=> true

type ShouldBeBar = IfNever<'not never', 'foo', 'bar'>;
//=> 'bar'

```

@category Type Guard
@category Utilities
*/
type IfNever<T, TypeIfNever = true, TypeIfNotNever = false> = (IsNever<T> extends true ? TypeIfNever : TypeIfNotNever);
type NoInfer$1<T> = T extends infer U ? U : never;
/**
Returns a boolean for whether the given type is `any`.

@link https://stackoverflow.com/a/49928360/1490091

Useful in type utilities, such as disallowing `any`s to be passed to a function.

@example
```

import type {IsAny} from 'type-fest';

const typedObject = {a: 1, b: 2} as const;
const anyObject: any = {a: 1, b: 2};

function get<O extends (IsAny<O> extends true ? {} : Record<string, number>), K extends keyof O = keyof O>(obj: O, key: K) {
return obj[key];
}

const typedA = get(typedObject, 'a');
//=> 1

const anyA = get(anyObject, 'a');
//=> any

```

@category Type Guard
@category Utilities
*/
type IsAny<T> = 0 extends 1 & NoInfer$1<T> ? true : false;
/**
Returns a boolean for whether the two given types are equal.

@link https://github.com/microsoft/TypeScript/issues/27024#issuecomment-421529650
@link https://stackoverflow.com/questions/68961864/how-does-the-equals-work-in-typescript/68963796#68963796

Use-cases:
- If you want to make a conditional branch based on the result of a comparison of two types.

@example
```

import type {IsEqual} from 'type-fest';

// This type returns a boolean for whether the given array includes the given item.
// `IsEqual` is used to compare the given array at position 0 and the given item and then return true if they are equal.
type Includes<Value extends readonly any[], Item> =
Value extends readonly [Value[0], ...infer rest]
? IsEqual<Value[0], Item> extends true
? true
: Includes<rest, Item>
: false;

```

@category Type Guard
@category Utilities
*/
type IsEqual<A, B> = (<G>() => G extends A & G | G ? 1 : 2) extends (<G>() => G extends B & G | G ? 1 : 2) ? true : false;
/**
Useful to flatten the type output to improve type hints shown in editors. And also to transform an interface into a type to aide with assignability.

@example
```

import type {Simplify} from 'type-fest';

type PositionProps = {
top: number;
left: number;
};

type SizeProps = {
width: number;
height: number;
};

// In your editor, hovering over `Props` will show a flattened object with all the properties.
type Props = Simplify<PositionProps & SizeProps>;

```

Sometimes it is desired to pass a value as a function argument that has a different type. At first inspection it may seem assignable, and then you discover it is not because the `value`'s type definition was defined as an interface. In the following example, `fn` requires an argument of type `Record<string, unknown>`. If the value is defined as a literal, then it is assignable. And if the `value` is defined as type using the `Simplify` utility the value is assignable.  But if the `value` is defined as an interface, it is not assignable because the interface is not sealed and elsewhere a non-string property could be added to the interface.

If the type definition must be an interface (perhaps it was defined in a third-party npm package), then the `value` can be defined as `const value: Simplify<SomeInterface> = ...`. Then `value` will be assignable to the `fn` argument.  Or the `value` can be cast as `Simplify<SomeInterface>` if you can't re-declare the `value`.

@example
```

import type {Simplify} from 'type-fest';

interface SomeInterface {
foo: number;
bar?: string;
baz: number | undefined;
}

type SomeType = {
foo: number;
bar?: string;
baz: number | undefined;
};

const literal = {foo: 123, bar: 'hello', baz: 456};
const someType: SomeType = literal;
const someInterface: SomeInterface = literal;

function fn(object: Record<string, unknown>): void {}

fn(literal); // Good: literal object type is sealed
fn(someType); // Good: type is sealed
fn(someInterface); // Error: Index signature for type 'string' is missing in type 'someInterface'. Because `interface` can be re-opened
fn(someInterface as Simplify<SomeInterface>); // Good: transform an `interface` into a `type`

```

@link https://github.com/microsoft/TypeScript/issues/15300
@see SimplifyDeep
@category Object
*/
type Simplify<T> = {
	[KeyType in keyof T]: T[KeyType];
} & {};
/**
Omit any index signatures from the given object type, leaving only explicitly defined properties.

This is the counterpart of `PickIndexSignature`.

Use-cases:
- Remove overly permissive signatures from third-party types.

This type was taken from this [StackOverflow answer](https://stackoverflow.com/a/68261113/420747).

It relies on the fact that an empty object (`{}`) is assignable to an object with just an index signature, like `Record<string, unknown>`, but not to an object with explicitly defined keys, like `Record<'foo' | 'bar', unknown>`.

(The actual value type, `unknown`, is irrelevant and could be any type. Only the key type matters.)

```

const indexed: Record<string, unknown> = {}; // Allowed

const keyed: Record<'foo', unknown> = {}; // Error
// => TS2739: Type '{}' is missing the following properties from type 'Record<"foo" | "bar", unknown>': foo, bar

```

Instead of causing a type error like the above, you can also use a [conditional type](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html) to test whether a type is assignable to another:

```

type Indexed = {} extends Record<string, unknown>
? '✅ `{}` is assignable to `Record<string, unknown>`'
: '❌ `{}` is NOT assignable to `Record<string, unknown>`';
// => '✅ `{}` is assignable to `Record<string, unknown>`'

type Keyed = {} extends Record<'foo' | 'bar', unknown>
? "✅ `{}` is assignable to `Record<'foo' | 'bar', unknown>`"
: "❌ `{}` is NOT assignable to `Record<'foo' | 'bar', unknown>`";
// => "❌ `{}` is NOT assignable to `Record<'foo' | 'bar', unknown>`"

```

Using a [mapped type](https://www.typescriptlang.org/docs/handbook/2/mapped-types.html#further-exploration), you can then check for each `KeyType` of `ObjectType`...

```

import type {OmitIndexSignature} from 'type-fest';

type OmitIndexSignature<ObjectType> = {
[KeyType in keyof ObjectType // Map each key of `ObjectType`...
]: ObjectType[KeyType]; // ...to its original value, i.e. `OmitIndexSignature<Foo> == Foo`.
};

```

...whether an empty object (`{}`) would be assignable to an object with that `KeyType` (`Record<KeyType, unknown>`)...

```

import type {OmitIndexSignature} from 'type-fest';

type OmitIndexSignature<ObjectType> = {
[KeyType in keyof ObjectType
// Is `{}` assignable to `Record<KeyType, unknown>`?
as {} extends Record<KeyType, unknown>
? ... // ✅ `{}` is assignable to `Record<KeyType, unknown>`
: ... // ❌ `{}` is NOT assignable to `Record<KeyType, unknown>`
]: ObjectType[KeyType];
};

```

If `{}` is assignable, it means that `KeyType` is an index signature and we want to remove it. If it is not assignable, `KeyType` is a "real" key and we want to keep it.

@example
```

import type {OmitIndexSignature} from 'type-fest';

interface Example {
// These index signatures will be removed.
[x: string]: any
[x: number]: any
[x: symbol]: any
[x: `head-${string}`]: string
[x: `${string}-tail`]: string
[x: `head-${string}-tail`]: string
[x: `${bigint}`]: string
[x: `embedded-${number}`]: string

    // These explicitly defined keys will remain.
    foo: 'bar';
    qux?: 'baz';

}

type ExampleWithoutIndexSignatures = OmitIndexSignature<Example>;
// => { foo: 'bar'; qux?: 'baz' | undefined; }

```

@see PickIndexSignature
@category Object
*/
type OmitIndexSignature<ObjectType> = {
	[KeyType in keyof ObjectType as {} extends Record<KeyType, unknown> ? never : KeyType]: ObjectType[KeyType];
};
/**
Pick only index signatures from the given object type, leaving out all explicitly defined properties.

This is the counterpart of `OmitIndexSignature`.

@example
```

import type {PickIndexSignature} from 'type-fest';

declare const symbolKey: unique symbol;

type Example = {
// These index signatures will remain.
[x: string]: unknown;
[x: number]: unknown;
[x: symbol]: unknown;
[x: `head-${string}`]: string;
[x: `${string}-tail`]: string;
[x: `head-${string}-tail`]: string;
[x: `${bigint}`]: string;
[x: `embedded-${number}`]: string;

    // These explicitly defined keys will be removed.
    ['kebab-case-key']: string;
    [symbolKey]: string;
    foo: 'bar';
    qux?: 'baz';

};

type ExampleIndexSignature = PickIndexSignature<Example>;
// {
// [x: string]: unknown;
// [x: number]: unknown;
// [x: symbol]: unknown;
// [x: `head-${string}`]: string;
// [x: `${string}-tail`]: string;
// [x: `head-${string}-tail`]: string;
// [x: `${bigint}`]: string;
// [x: `embedded-${number}`]: string;
// }

```

@see OmitIndexSignature
@category Object
*/
type PickIndexSignature<ObjectType> = {
	[KeyType in keyof ObjectType as {} extends Record<KeyType, unknown> ? KeyType : never]: ObjectType[KeyType];
};
// Merges two objects without worrying about index signatures.
type SimpleMerge<Destination, Source> = {
	[Key in keyof Destination as Key extends keyof Source ? never : Key]: Destination[Key];
} & Source;
/**
Merge two types into a new type. Keys of the second type overrides keys of the first type.

@example
```

import type {Merge} from 'type-fest';

interface Foo {
[x: string]: unknown;
[x: number]: unknown;
foo: string;
bar: symbol;
}

type Bar = {
[x: number]: number;
[x: symbol]: unknown;
bar: Date;
baz: boolean;
};

export type FooBar = Merge<Foo, Bar>;
// => {
// [x: string]: unknown;
// [x: number]: number;
// [x: symbol]: unknown;
// foo: string;
// bar: Date;
// baz: boolean;
// }

```

@category Object
*/
type Merge<Destination, Source> = Simplify<SimpleMerge<PickIndexSignature<Destination>, PickIndexSignature<Source>> & SimpleMerge<OmitIndexSignature<Destination>, OmitIndexSignature<Source>>>;
/**
An if-else-like type that resolves depending on whether the given type is `any`.

@see {@link IsAny}

@example
```

import type {IfAny} from 'type-fest';

type ShouldBeTrue = IfAny<any>;
//=> true

type ShouldBeBar = IfAny<'not any', 'foo', 'bar'>;
//=> 'bar'

```

@category Type Guard
@category Utilities
*/
type IfAny<T, TypeIfAny = true, TypeIfNotAny = false> = (IsAny<T> extends true ? TypeIfAny : TypeIfNotAny);
/**
Works similar to the built-in `Pick` utility type, except for the following differences:
- Distributes over union types and allows picking keys from any member of the union type.
- Primitives types are returned as-is.
- Picks all keys if `Keys` is `any`.
- Doesn't pick `number` from a `string` index signature.

@example
```

type ImageUpload = {
url: string;
size: number;
thumbnailUrl: string;
};

type VideoUpload = {
url: string;
duration: number;
encodingFormat: string;
};

// Distributes over union types and allows picking keys from any member of the union type
type MediaDisplay = HomomorphicPick<ImageUpload | VideoUpload, "url" | "size" | "duration">;
//=> {url: string; size: number} | {url: string; duration: number}

// Primitive types are returned as-is
type Primitive = HomomorphicPick<string | number, 'toUpperCase' | 'toString'>;
//=> string | number

// Picks all keys if `Keys` is `any`
type Any = HomomorphicPick<{a: 1; b: 2} | {c: 3}, any>;
//=> {a: 1; b: 2} | {c: 3}

// Doesn't pick `number` from a `string` index signature
type IndexSignature = HomomorphicPick<{[k: string]: unknown}, number>;
//=> {}
\*/
type HomomorphicPick<T, Keys extends KeysOfUnion<T>> = {
[P in keyof T as Extract<P, Keys>]: T[P];
};
/\*\*
Merges user specified options with default options.

@example

```
type PathsOptions = {maxRecursionDepth?: number; leavesOnly?: boolean};
type DefaultPathsOptions = {maxRecursionDepth: 10; leavesOnly: false};
type SpecifiedOptions = {leavesOnly: true};

type Result = ApplyDefaultOptions<PathsOptions, DefaultPathsOptions, SpecifiedOptions>;
//=> {maxRecursionDepth: 10; leavesOnly: true}
```

@example

```
// Complains if default values are not provided for optional options

type PathsOptions = {maxRecursionDepth?: number; leavesOnly?: boolean};
type DefaultPathsOptions = {maxRecursionDepth: 10};
type SpecifiedOptions = {};

type Result = ApplyDefaultOptions<PathsOptions, DefaultPathsOptions, SpecifiedOptions>;
//                                              ~~~~~~~~~~~~~~~~~~~
// Property 'leavesOnly' is missing in type 'DefaultPathsOptions' but required in type '{ maxRecursionDepth: number; leavesOnly: boolean; }'.
```

@example

```
// Complains if an option's default type does not conform to the expected type

type PathsOptions = {maxRecursionDepth?: number; leavesOnly?: boolean};
type DefaultPathsOptions = {maxRecursionDepth: 10; leavesOnly: 'no'};
type SpecifiedOptions = {};

type Result = ApplyDefaultOptions<PathsOptions, DefaultPathsOptions, SpecifiedOptions>;
//                                              ~~~~~~~~~~~~~~~~~~~
// Types of property 'leavesOnly' are incompatible. Type 'string' is not assignable to type 'boolean'.
```

@example

```
// Complains if an option's specified type does not conform to the expected type

type PathsOptions = {maxRecursionDepth?: number; leavesOnly?: boolean};
type DefaultPathsOptions = {maxRecursionDepth: 10; leavesOnly: false};
type SpecifiedOptions = {leavesOnly: 'yes'};

type Result = ApplyDefaultOptions<PathsOptions, DefaultPathsOptions, SpecifiedOptions>;
//                                                                   ~~~~~~~~~~~~~~~~
// Types of property 'leavesOnly' are incompatible. Type 'string' is not assignable to type 'boolean'.
```

\*/
type ApplyDefaultOptions<Options extends object, Defaults extends Simplify<Omit<Required<Options>, RequiredKeysOf<Options>> & Partial<Record<RequiredKeysOf<Options>, never>>>, SpecifiedOptions extends Options> = IfAny<SpecifiedOptions, Defaults, IfNever<SpecifiedOptions, Defaults, Simplify<Merge<Defaults, {
[Key in keyof SpecifiedOptions as Key extends OptionalKeysOf<Options> ? Extract<SpecifiedOptions[Key], undefined> extends never ? Key : never : Key]: SpecifiedOptions[Key];
}> & Required<Options>> // `& Required<Options>` ensures that `ApplyDefaultOptions<SomeOption, ...>` is always assignable to `Required<SomeOption>`

> > ;
> > /\*\*
> > Filter out keys from an object.

Returns `never` if `Exclude` is strictly equal to `Key`.
Returns `never` if `Key` extends `Exclude`.
Returns `Key` otherwise.

@example

```
type Filtered = Filter<'foo', 'foo'>;
//=> never
```

@example

```
type Filtered = Filter<'bar', string>;
//=> never
```

@example

```
type Filtered = Filter<'bar', 'foo'>;
//=> 'bar'
```

@see {Except}
\*/
type Filter<KeyType, ExcludeType> = IsEqual<KeyType, ExcludeType> extends true ? never : (KeyType extends ExcludeType ? never : KeyType);
type ExceptOptions = {
/\*\*
Disallow assigning non-specified properties.

    Note that any omitted properties in the resulting type will be present in autocomplete as `undefined`.

    @default false
    */
    requireExactProps?: boolean;

};
type DefaultExceptOptions = {
requireExactProps: false;
};
/\*\*
Create a type from an object type without certain keys.

We recommend setting the `requireExactProps` option to `true`.

This type is a stricter version of [`Omit`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-5.html#the-omit-helper-type). The `Omit` type does not restrict the omitted keys to be keys present on the given type, while `Except` does. The benefits of a stricter type are avoiding typos and allowing the compiler to pick up on rename refactors automatically.

This type was proposed to the TypeScript team, which declined it, saying they prefer that libraries implement stricter versions of the built-in types ([microsoft/TypeScript#30825](https://github.com/microsoft/TypeScript/issues/30825#issuecomment-523668235)).

@example

```
import type {Except} from 'type-fest';

type Foo = {
	a: number;
	b: string;
};

type FooWithoutA = Except<Foo, 'a'>;
//=> {b: string}

const fooWithoutA: FooWithoutA = {a: 1, b: '2'};
//=> errors: 'a' does not exist in type '{ b: string; }'

type FooWithoutB = Except<Foo, 'b', {requireExactProps: true}>;
//=> {a: number} & Partial<Record<"b", never>>

const fooWithoutB: FooWithoutB = {a: 1, b: '2'};
//=> errors at 'b': Type 'string' is not assignable to type 'undefined'.

// The `Omit` utility type doesn't work when omitting specific keys from objects containing index signatures.

// Consider the following example:

type UserData = {
	[metadata: string]: string;
	email: string;
	name: string;
	role: 'admin' | 'user';
};

// `Omit` clearly doesn't behave as expected in this case:
type PostPayload = Omit<UserData, 'email'>;
//=> type PostPayload = { [x: string]: string; [x: number]: string; }

// In situations like this, `Except` works better.
// It simply removes the `email` key while preserving all the other keys.
type PostPayload = Except<UserData, 'email'>;
//=> type PostPayload = { [x: string]: string; name: string; role: 'admin' | 'user'; }
```

@category Object
\*/
type Except<ObjectType, KeysType extends keyof ObjectType, Options extends ExceptOptions = {}> = \_Except<ObjectType, KeysType, ApplyDefaultOptions<ExceptOptions, DefaultExceptOptions, Options>>;
type \_Except<ObjectType, KeysType extends keyof ObjectType, Options extends Required<ExceptOptions>> = {
[KeyType in keyof ObjectType as Filter<KeyType, KeysType>]: ObjectType[KeyType];
} & (Options["requireExactProps"] extends true ? Partial<Record<KeysType, never>> : {});
/\*\*
Create a type that makes the given keys optional. The remaining keys are kept as is. The sister of the `SetRequired` type.

Use-case: You want to define a single model where the only thing that changes is whether or not some of the keys are optional.

@example

```
import type {SetOptional} from 'type-fest';

type Foo = {
	a: number;
	b?: string;
	c: boolean;
}

type SomeOptional = SetOptional<Foo, 'b' | 'c'>;
// type SomeOptional = {
// 	a: number;
// 	b?: string; // Was already optional and still is.
// 	c?: boolean; // Is now optional.
// }
```

@category Object
\*/
type SetOptional<BaseType, Keys extends keyof BaseType> = BaseType extends unknown // To distribute `BaseType` when it's a union type.
? Simplify<
// Pick just the keys that are readonly from the base type.
Except<BaseType, Keys> &
// Pick the keys that should be mutable from the base type and make them mutable.
Partial<HomomorphicPick<BaseType, Keys>>> : never;
/\*\*

- This file has utilities to create GraphQL clients
- that consume the types generated by the preset.
  \*/
  /\*\*
- A generic type for `variables` in GraphQL clients
  \*/
  type GenericVariables = ExecutionArgs["variableValues"];
  /\*\*
- Use this type to make parameters optional in GraphQL clients
- when no variables need to be passed.
  \*/
  type EmptyVariables = {
  [key: string]: never;
  };
  /\*\*
- GraphQL client's generic operation interface.
  \*/
  interface CodegenOperations {
  [key: string]: any;
  }
  /\*\*
- Used as the return type for GraphQL clients. It picks
- the return type from the generated operation types.
- @example
- graphqlQuery: (...) => Promise<ClientReturn<...>>
- graphqlQuery: (...) => Promise<{data: ClientReturn<...>}>
  \*/
  type ClientReturn<GeneratedOperations extends CodegenOperations, RawGqlString extends string, OverrideReturnType extends any = never> = IsNever<OverrideReturnType> extends true ? RawGqlString extends keyof GeneratedOperations ? GeneratedOperations[RawGqlString]["return"] : any : OverrideReturnType;
  /\*\*
- Checks if the generated variables for an operation
- are optional or required.
  \*/
  type IsOptionalVariables<VariablesParam, OptionalVariableNames extends string = never, VariablesWithoutOptionals = Omit<VariablesParam, OptionalVariableNames>> = VariablesWithoutOptionals extends EmptyVariables ? true : GenericVariables extends VariablesParam ? true : Partial<VariablesWithoutOptionals> extends VariablesWithoutOptionals ? true : false;
  /\*\*
- Used as the type for the GraphQL client's variables. It checks
- the generated operation types to see if variables are optional.
- @example
- graphqlQuery: (query: string, param: ClientVariables<...>) => Promise<...>
- Where `param` is required.
  \*/
  type ClientVariables<GeneratedOperations extends CodegenOperations, RawGqlString extends string, OptionalVariableNames extends string = never, VariablesKey extends string = "variables", GeneratedVariables = RawGqlString extends keyof GeneratedOperations ? SetOptional<GeneratedOperations[RawGqlString]["variables"], Extract<keyof GeneratedOperations[RawGqlString]["variables"], OptionalVariableNames>> : GenericVariables, VariablesWrapper = Record<VariablesKey, GeneratedVariables>> = IsOptionalVariables<GeneratedVariables, OptionalVariableNames> extends true ? Partial<VariablesWrapper> : VariablesWrapper;
  /\*\*
- Similar to ClientVariables, but makes the whole wrapper optional:
- @example
- graphqlQuery: (query: string, ...params: ClientVariablesInRestParams<...>) => Promise<...>
- Where the first item in `params` might be optional depending on the query.
  \*/
  type ClientVariablesInRestParams<GeneratedOperations extends CodegenOperations, RawGqlString extends string, OtherParams extends Record<string, any> = {}, OptionalVariableNames extends string = never, ProcessedVariables = OtherParams & ClientVariables<GeneratedOperations, RawGqlString, OptionalVariableNames>> = Partial<OtherParams> extends OtherParams ? IsOptionalVariables<GeneratedOperations[RawGqlString]["variables"], OptionalVariableNames> extends true ? [
  ProcessedVariables?
  ] : [
  ProcessedVariables
  ] : [
  ProcessedVariables
  ];

declare class GraphQLError extends Error {
/**
_ If an error can be associated to a particular point in the requested
_ GraphQL document, it should contain a list of locations.
\*/
locations?: Array<{
line: number;
column: number;
}>;
/**
_ If an error can be associated to a particular field in the GraphQL result,
_ it _must_ contain an entry with the key `path` that details the path of
_ the response field which experienced the error. This allows clients to
_ identify whether a null result is intentional or caused by a runtime error.
_/
path?: Array<string | number>;
/\*\*
_ Reserved for implementors to extend the protocol however they see fit,
_ and hence there are no additional restrictions on its contents.
_/
extensions?: {
[key: string]: unknown;
};
constructor(message?: string, options?: Pick<GraphQLError, 'locations' | 'path' | 'extensions' | 'stack' | 'cause'> & {
query?: string;
queryVariables?: GenericVariables;
requestId?: string | null;
clientOperation?: string;
});
get [Symbol.toStringTag](): string;
/**
_ Note: `toString()` is internally used by `console.log(...)` / `console.error(...)`
_ when ingesting logs in Oxygen production. Therefore, we want to make sure that
_ the error message is as informative as possible instead of `[object Object]`.
_/
toString(): string;
/**
_ Note: toJSON`is internally used by`JSON.stringify(...)`.
_ The most common scenario when this error instance is going to be stringified is
_ when it's passed to Remix' `json` and `defer` functions: e.g. `{promise: storefront.query(...)}`.
_ In this situation, we don't want to expose private error information to the browser so we only
_ do it in development.
_/
toJSON(): Pick<GraphQLError, "message" | "locations" | "path" | "extensions" | "stack" | "name">;
}

type CrossRuntimeRequest = {
url?: string;
method?: string;
headers: {
get?: (key: string) => string | null | undefined;
[key: string]: any;
};
};

type DataFunctionValue = Response | NonNullable<unknown> | null;
type JsonGraphQLError$1 = ReturnType<GraphQLError['toJSON']>;
type Buyer = Partial<BuyerInput>;
type CustomerAPIResponse<ReturnType> = {
data: ReturnType;
errors: Array<{
message: string;
locations?: Array<{
line: number;
column: number;
}>;
path?: Array<string>;
extensions: {
code: string;
};
}>;
extensions: {
cost: {
requestQueryCost: number;
actualQueryCakes: number;
throttleStatus: {
maximumAvailable: number;
currentAvailable: number;
restoreRate: number;
};
};
};
};
interface CustomerAccountQueries {
}
interface CustomerAccountMutations {
}
type LoginOptions = {
uiLocales?: LanguageCode;
locale?: string;
countryCode?: CountryCode;
acrValues?: string;
loginHint?: string;
loginHintMode?: string;
};
type LogoutOptions = {
/** The url to redirect customer to after logout, should be a relative URL. This url will need to included in Customer Account API's application setup for logout URI. The default value is current app origin, which is automatically setup in admin when using `--customer-account-push` flag with dev. \*/
postLogoutRedirectUri?: string;
/** Add custom headers to the logout redirect. _/
headers?: HeadersInit;
/\*\* If true, custom data in the session will not be cleared on logout. _/
keepSession?: boolean;
};
type CustomerAccount = {
/** The i18n configuration for Customer Account API \*/
i18n: {
language: LanguageCode;
};
/** Start the OAuth login flow. This function should be called and returned from a Remix loader.
_ It redirects the customer to a Shopify login domain. It also defined the final path the customer
_ lands on at the end of the oAuth flow with the value of the `return_to` query param. (This is
_ automatically setup unless `customAuthStatusHandler` option is in use)
_
_ @param options.uiLocales - The displayed language of the login page. Only support for the following languages:
_ `en`, `fr`, `cs`, `da`, `de`, `es`, `fi`, `it`, `ja`, `ko`, `nb`, `nl`, `pl`, `pt-BR`, `pt-PT`,
_ `sv`, `th`, `tr`, `vi`, `zh-CN`, `zh-TW`. If supplied any other language code, it will default to `en`.
_ _/
login: (options?: LoginOptions) => Promise<Response>;
/\*\* On successful login, the customer redirects back to your app. This function validates the OAuth response and exchanges the authorization code for an access token and refresh token. It also persists the tokens on your session. This function should be called and returned from the Remix loader configured as the redirect URI within the Customer Account API settings in admin. _/
authorize: () => Promise<Response>;
/** Returns if the customer is logged in. It also checks if the access token is expired and refreshes it if needed. \*/
isLoggedIn: () => Promise<boolean>;
/** Check for a not logged in customer and redirect customer to login page. The redirect can be overwritten with `customAuthStatusHandler` option. _/
handleAuthStatus: () => Promise<void>;
/\*\* Returns CustomerAccessToken if the customer is logged in. It also run a expiry check and does a token refresh if needed. _/
getAccessToken: () => Promise<string | undefined>;
/** Creates the fully-qualified URL to your store's GraphQL endpoint.\*/
getApiUrl: () => string;
/** Logout the customer by clearing the session and redirecting to the login domain. It should be called and returned from a Remix action. The path app should redirect to after logout can be setup in Customer Account API settings in admin. \*
_ @param options.postLogoutRedirectUri - The url to redirect customer to after logout, should be a relative URL. This url will need to included in Customer Account API's application setup for logout URI. The default value is current app origin, which is automatically setup in admin when using `--customer-account-push` flag with dev.
_ @param options.headers - These will be passed along to the logout redirect. You can use these to set/clear cookies on logout, like the cart.
_ @param options.keepSession - If true, custom data in the session will not be cleared on logout.
_ _/
logout: (options?: LogoutOptions) => Promise<Response>;
/\*\* Execute a GraphQL query against the Customer Account API. This method execute `handleAuthStatus()` ahead of query. _/
query: <OverrideReturnType extends any = never, RawGqlString extends string = string>(query: RawGqlString, ...options: ClientVariablesInRestParams<CustomerAccountQueries, RawGqlString>) => Promise<Omit<CustomerAPIResponse<ClientReturn<CustomerAccountQueries, RawGqlString, OverrideReturnType>>, 'errors'> & {
errors?: JsonGraphQLError$1[];
}>;
/** Execute a GraphQL mutation against the Customer Account API. This method execute `handleAuthStatus()` ahead of mutation. \*/
mutate: <OverrideReturnType extends any = never, RawGqlString extends string = string>(mutation: RawGqlString, ...options: ClientVariablesInRestParams<CustomerAccountMutations, RawGqlString>) => Promise<Omit<CustomerAPIResponse<ClientReturn<CustomerAccountMutations, RawGqlString, OverrideReturnType>>, 'errors'> & {
errors?: JsonGraphQLError$1[];
}>;
/** Set buyer information into session._/
setBuyer: (buyer: Buyer) => void;
/\*\* Get buyer token and company location id from session._/
getBuyer: () => Promise<Buyer>;
/** Deprecated. Please use setBuyer. Set buyer information into session.\*/
UNSTABLE_setBuyer: (buyer: Buyer) => void;
/** Deprecated. Please use getBuyer. Get buyer token and company location id from session._/
UNSTABLE_getBuyer: () => Promise<Buyer>;
};
type CustomerAccountOptions = {
/\*\* The client requires a session to persist the auth and refresh token. By default Hydrogen ships with cookie session storage, but you can use [another session storage](https://remix.run/docs/en/main/utils/sessions) implementation. _/
session: HydrogenSession;
/** Unique UUID prefixed with `shp_` associated with the application, this should be visible in the customer account api settings in the Hydrogen admin channel. Mock.shop doesn't automatically supply customerAccountId. Use `npx shopify hydrogen env pull` to link your store credentials. \*/
customerAccountId: string;
/** The shop id. Mock.shop doesn't automatically supply shopId. Use `npx shopify hydrogen env pull` to link your store credentials _/
shopId: string;
/\*\* Override the version of the API _/
customerApiVersion?: string;
/** The object for the current Request. It should be provided by your platform. \*/
request: CrossRuntimeRequest;
/** The waitUntil function is used to keep the current request/response lifecycle alive even after a response has been sent. It should be provided by your platform. _/
waitUntil?: WaitUntil;
/\*\* This is the route in your app that authorizes the customer after logging in. Make sure to call `customer.authorize()` within the loader on this route. It defaults to `/account/authorize`. _/
authUrl?: string;
/** Use this method to overwrite the default logged-out redirect behavior. The default handler [throws a redirect](https://remix.run/docs/en/main/utils/redirect#:~:text=!session) to `/account/login` with current path as `return_to` query param. \*/
customAuthStatusHandler?: () => DataFunctionValue;
/** Whether it should print GraphQL errors automatically. Defaults to true _/
logErrors?: boolean | ((error?: Error) => boolean);
/\*\* The path to redirect to after login. Defaults to `/account`. _/
defaultRedirectPath?: string;
/** The path to login. Defaults to `/account/login`. \*/
loginPath?: string;
/** The oauth authorize path. Defaults to `/account/authorize`. _/
authorizePath?: string;
/\*\* Deprecated. `unstableB2b` is now stable. Please remove. _/
unstableB2b?: boolean;
/\*_ Localization data. _/
language?: LanguageCode;
};

type CartGetProps = {
/**
_ The cart ID.
_ @default cart.getCartId();
\*/
cartId?: string;
/**
_ The country code.
_ @default storefront.i18n.country
_/
country?: CountryCode$1;
/\*\*
_ The language code.
_ @default storefront.i18n.language
_/
language?: LanguageCode$1;
/**
_ The number of cart lines to be returned.
_ @default 100
\*/
numCartLines?: number;
/**
_ Visitor consent preferences for the Storefront API's @inContext directive.
_
_ **Most Hydrogen storefronts do NOT need this.** If you're using Hydrogen's
_ analytics provider or Shopify's Customer Privacy API (including third-party
_ consent services integrated with it), consent is handled automatically.
_
_ This option exists for Storefront API parity and is primarily intended for
_ non-Hydrogen integrations like Checkout Kit that manage consent outside
_ Shopify's standard consent flow.
_
_ When provided, consent is encoded into the cart's checkoutUrl via the \_cs parameter.
_/
visitorConsent?: VisitorConsent$1;
};
type CartGetFunction = (cartInput?: CartGetProps) => Promise<CartReturn | null>;
type CartGetOptions = CartQueryOptions & {
/\*\*
_ The customer account client instance created by [`createCustomerAccountClient`](docs/api/hydrogen/latest/utilities/createcustomeraccountclient).
_/
customerAccount?: CustomerAccount;
};
declare function cartGetDefault({ storefront, customerAccount, getCartId, cartFragment, }: CartGetOptions): CartGetFunction;

type CartCreateFunction = (input: CartInput, optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartCreateDefault(options: CartQueryOptions): CartCreateFunction;

type CartLinesAddFunction = (lines: Array<CartLineInput>, optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartLinesAddDefault(options: CartQueryOptions): CartLinesAddFunction;

type CartLinesUpdateFunction = (lines: CartLineUpdateInput[], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartLinesUpdateDefault(options: CartQueryOptions): CartLinesUpdateFunction;

type CartLinesRemoveFunction = (lineIds: string[], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartLinesRemoveDefault(options: CartQueryOptions): CartLinesRemoveFunction;

type CartDiscountCodesUpdateFunction = (discountCodes: string[], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartDiscountCodesUpdateDefault(options: CartQueryOptions): CartDiscountCodesUpdateFunction;

type CartBuyerIdentityUpdateFunction = (buyerIdentity: CartBuyerIdentityInput, optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartBuyerIdentityUpdateDefault(options: CartQueryOptions): CartBuyerIdentityUpdateFunction;

type CartNoteUpdateFunction = (note: string, optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartNoteUpdateDefault(options: CartQueryOptions): CartNoteUpdateFunction;

type CartSelectedDeliveryOptionsUpdateFunction = (selectedDeliveryOptions: CartSelectedDeliveryOptionInput[], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartSelectedDeliveryOptionsUpdateDefault(options: CartQueryOptions): CartSelectedDeliveryOptionsUpdateFunction;

type CartAttributesUpdateFunction = (attributes: AttributeInput[], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartAttributesUpdateDefault(options: CartQueryOptions): CartAttributesUpdateFunction;

type CartMetafieldsSetFunction = (metafields: MetafieldWithoutOwnerId[], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartMetafieldsSetDefault(options: CartQueryOptions): CartMetafieldsSetFunction;

type CartMetafieldDeleteFunction = (key: Scalars['String']['input'], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartMetafieldDeleteDefault(options: CartQueryOptions): CartMetafieldDeleteFunction;

type CartGiftCardCodesUpdateFunction = (giftCardCodes: string[], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
/\*\*

- Updates (replaces) gift card codes in the cart.
-
- To add codes without replacing, use `cartGiftCardCodesAdd` (API 2025-10+).
-
- @param {CartQueryOptions} options - Cart query options including storefront client and cart fragment.
- @returns {CartGiftCardCodesUpdateFunction} - Function accepting gift card codes array and optional parameters.
-
- @example Replace all gift card codes
- const updateGiftCardCodes = cartGiftCardCodesUpdateDefault({ storefront, getCartId });
- await updateGiftCardCodes(['SUMMER2025', 'WELCOME10']);
  \*/
  declare function cartGiftCardCodesUpdateDefault(options: CartQueryOptions): CartGiftCardCodesUpdateFunction;

type CartGiftCardCodesAddFunction = (giftCardCodes: string[], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
/\*\*

- Adds gift card codes to the cart without replacing existing ones.
-
- This function sends a mutation to the Storefront API to add one or more gift card codes to the cart.
- Unlike `cartGiftCardCodesUpdate` which replaces all codes, this mutation appends new codes to existing ones.
-
- @param {CartQueryOptions} options - The options for the cart query, including the storefront API client and cart fragment.
- @returns {CartGiftCardCodesAddFunction} - A function that takes an array of gift card codes and optional parameters, and returns the result of the API call.
-
- @example Add gift card codes
- const addGiftCardCodes = cartGiftCardCodesAddDefault({ storefront, getCartId });
- await addGiftCardCodes(['SUMMER2025', 'WELCOME10']);
  \*/
  declare function cartGiftCardCodesAddDefault(options: CartQueryOptions): CartGiftCardCodesAddFunction;

type CartGiftCardCodesRemoveFunction = (appliedGiftCardIds: string[], optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
declare function cartGiftCardCodesRemoveDefault(options: CartQueryOptions): CartGiftCardCodesRemoveFunction;

type CartDeliveryAddressesAddFunction = (addresses: Array<CartSelectableAddressInput>, optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
/\*\*

- Adds delivery addresses to the cart.
-
- This function sends a mutation to the storefront API to add one or more delivery addresses to the cart.
- It returns the result of the mutation, including any errors that occurred.
-
- @param {CartQueryOptions} options - The options for the cart query, including the storefront API client and cart fragment.
- @returns {CartDeliveryAddressAddFunction} - A function that takes an array of addresses and optional parameters, and returns the result of the API call.
-
- @example
- const addDeliveryAddresses = cartDeliveryAddressesAddDefault({ storefront, getCartId });
- const result = await addDeliveryAddresses([
- {
-      address1: '123 Main St',
-      city: 'Anytown',
-      countryCode: 'US'
-      // other address fields...
- }
- ], { someOptionalParam: 'value' }
- );
  \*/
  declare function cartDeliveryAddressesAddDefault(options: CartQueryOptions): CartDeliveryAddressesAddFunction;

type CartDeliveryAddressesRemoveFunction = (addressIds: Array<Scalars['ID']['input']> | Array<string>, optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
/\*\*

- Removes delivery addresses from the cart.
-
- This function sends a mutation to the storefront API to remove one or more delivery addresses from the cart.
- It returns the result of the mutation, including any errors that occurred.
-
- @param {CartQueryOptions} options - The options for the cart query, including the storefront API client and cart fragment.
- @returns {CartDeliveryAddressRemoveFunction} - A function that takes an array of address IDs and optional parameters, and returns the result of the API call.
-
- @example
- const removeDeliveryAddresses = cartDeliveryAddressesRemoveDefault({ storefront, getCartId });
- const result = await removeDeliveryAddresses([
- "gid://shopify/<objectName>/10079785100"
- ],
- { someOptionalParam: 'value' });
  \*/
  declare function cartDeliveryAddressesRemoveDefault(options: CartQueryOptions): CartDeliveryAddressesRemoveFunction;

type CartDeliveryAddressesUpdateFunction = (addresses: Array<CartSelectableAddressUpdateInput>, optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
/\*\*

- Updates delivery addresses in the cart.
-
- Pass an empty array to clear all delivery addresses from the cart.
-
- @param {CartQueryOptions} options - The options for the cart query, including the storefront API client and cart fragment.
- @returns {CartDeliveryAddressUpdateFunction} - A function that takes an array of addresses and optional parameters, and returns the result of the API call.
-
- @example Clear all delivery addresses
- const updateAddresses = cartDeliveryAddressesUpdateDefault(cartQueryOptions);
- await updateAddresses([]);
-
- @example Update specific delivery addresses
- const updateAddresses = cartDeliveryAddressesUpdateDefault(cartQueryOptions);
- await updateAddresses([
  {
  "address": {
  "copyFromCustomerAddressId": "gid://shopify/<objectName>/10079785100",
  "deliveryAddress": {
  "address1": "<your-address1>",
  "address2": "<your-address2>",
  "city": "<your-city>",
  "company": "<your-company>",
  "countryCode": "AC",
  "firstName": "<your-firstName>",
  "lastName": "<your-lastName>",
  "phone": "<your-phone>",
  "provinceCode": "<your-provinceCode>",
  "zip": "<your-zip>"
  }
  },
  "id": "gid://shopify/<objectName>/10079785100",
  "oneTimeUse": true,
  "selected": true,
  "validationStrategy": "COUNTRY_CODE_ONLY"
  }
  ],{ someOptionalParam: 'value' });
  \*/
  declare function cartDeliveryAddressesUpdateDefault(options: CartQueryOptions): CartDeliveryAddressesUpdateFunction;

type CartDeliveryAddressesReplaceFunction = (addresses: Array<CartSelectableAddressInput>, optionalParams?: CartOptionalInput) => Promise<CartQueryDataReturn>;
/\*\*

- Replaces all delivery addresses on the cart.
-
- This function sends a mutation to the storefront API to replace all delivery addresses on the cart
- with the provided addresses. It returns the result of the mutation, including any errors that occurred.
-
- @param {CartQueryOptions} options - The options for the cart query, including the storefront API client and cart fragment.
- @returns {CartDeliveryAddressesReplaceFunction} - A function that takes an array of addresses and optional parameters, and returns the result of the API call.
-
- @example
- const replaceDeliveryAddresses = cartDeliveryAddressesReplaceDefault({ storefront, getCartId });
- const result = await replaceDeliveryAddresses([
- {
-      address: {
-        deliveryAddress: {
-          address1: '123 Main St',
-          city: 'Anytown',
-          countryCode: 'US'
-        }
-      },
-      selected: true
- }
- ], { someOptionalParam: 'value' }
- );
  \*/
  declare function cartDeliveryAddressesReplaceDefault(options: CartQueryOptions): CartDeliveryAddressesReplaceFunction;

type CartHandlerOptions = {
storefront: Storefront;
customerAccount?: CustomerAccount;
getCartId: () => string | undefined;
setCartId: (cartId: string) => Headers;
cartQueryFragment?: string;
cartMutateFragment?: string;
buyerIdentity?: CartBuyerIdentityInput;
};
type CustomMethodsBase = Record<string, Function>;
type CartHandlerOptionsWithCustom<TCustomMethods extends CustomMethodsBase> = CartHandlerOptions & {
customMethods?: TCustomMethods;
};
type HydrogenCart = {
get: ReturnType<typeof cartGetDefault>;
getCartId: () => string | undefined;
setCartId: (cartId: string) => Headers;
create: ReturnType<typeof cartCreateDefault>;
addLines: ReturnType<typeof cartLinesAddDefault>;
updateLines: ReturnType<typeof cartLinesUpdateDefault>;
removeLines: ReturnType<typeof cartLinesRemoveDefault>;
updateDiscountCodes: ReturnType<typeof cartDiscountCodesUpdateDefault>;
updateGiftCardCodes: ReturnType<typeof cartGiftCardCodesUpdateDefault>;
addGiftCardCodes: ReturnType<typeof cartGiftCardCodesAddDefault>;
removeGiftCardCodes: ReturnType<typeof cartGiftCardCodesRemoveDefault>;
updateBuyerIdentity: ReturnType<typeof cartBuyerIdentityUpdateDefault>;
updateNote: ReturnType<typeof cartNoteUpdateDefault>;
updateSelectedDeliveryOption: ReturnType<typeof cartSelectedDeliveryOptionsUpdateDefault>;
updateAttributes: ReturnType<typeof cartAttributesUpdateDefault>;
setMetafields: ReturnType<typeof cartMetafieldsSetDefault>;
deleteMetafield: ReturnType<typeof cartMetafieldDeleteDefault>;
/**
_ Adds delivery addresses to the cart.
_
_ This function sends a mutation to the storefront API to add one or more delivery addresses to the cart.
_ It returns the result of the mutation, including any errors that occurred. \*
_ @param {CartQueryOptions} options - The options for the cart query, including the storefront API client and cart fragment.
_ @returns {ReturnType<typeof cartDeliveryAddressesAddDefault>} - A function that takes an array of addresses and optional parameters, and returns the result of the API call. \*
_ @example
_ const result = await cart.addDeliveryAddresses(
_ [
_ {
_ address1: '123 Main St',
_ city: 'Anytown',
_ countryCode: 'US'
_ }
_ ],
_ { someOptionalParam: 'value' }
_ );
_/
addDeliveryAddresses: ReturnType<typeof cartDeliveryAddressesAddDefault>;
/**
_ Removes delivery addresses from the cart.
_
_ This function sends a mutation to the storefront API to remove one or more delivery addresses from the cart.
_ It returns the result of the mutation, including any errors that occurred. \*
_ @param {CartQueryOptions} options - The options for the cart query, including the storefront API client and cart fragment.
_ @returns {CartDeliveryAddressRemoveFunction} - A function that takes an array of address IDs and optional parameters, and returns the result of the API call. \*
_ @example
_ const result = await cart.removeDeliveryAddresses([

- "gid://shopify/<objectName>/10079785100"
- ],
  _ { someOptionalParam: 'value' });
  _/
  removeDeliveryAddresses: ReturnType<typeof cartDeliveryAddressesRemoveDefault>;
  /**
  _ Updates delivery addresses in the cart.
  _
  _ This function sends a mutation to the storefront API to update one or more delivery addresses in the cart.
  _ It returns the result of the mutation, including any errors that occurred. \*
  _ @param {CartQueryOptions} options - The options for the cart query, including the storefront API client and cart fragment.
  _ @returns {CartDeliveryAddressUpdateFunction} - A function that takes an array of addresses and optional parameters, and returns the result of the API call. \*
  _ const result = await cart.updateDeliveryAddresses([
  {
  "address": {
  "copyFromCustomerAddressId": "gid://shopify/<objectName>/10079785100",
  "deliveryAddress": {
  "address1": "<your-address1>",
  "address2": "<your-address2>",
  "city": "<your-city>",
  "company": "<your-company>",
  "countryCode": "AC",
  "firstName": "<your-firstName>",
  "lastName": "<your-lastName>",
  "phone": "<your-phone>",
  "provinceCode": "<your-provinceCode>",
  "zip": "<your-zip>"
  }
  },
  "id": "gid://shopify/<objectName>/10079785100",
  "oneTimeUse": true,
  "selected": true,
  "validationStrategy": "COUNTRY_CODE_ONLY"
  }
  ],{ someOptionalParam: 'value' });
  _/
  updateDeliveryAddresses: ReturnType<typeof cartDeliveryAddressesUpdateDefault>;
  /**
  _ Replaces all delivery addresses on the cart.
  _
  _ This function sends a mutation to the storefront API to replace all delivery addresses on the cart
  _ with the provided addresses. It returns the result of the mutation, including any errors that occurred. \*
  _ @param {CartQueryOptions} options - The options for the cart query, including the storefront API client and cart fragment.
  _ @returns {CartDeliveryAddressesReplaceFunction} - A function that takes an array of addresses and optional parameters, and returns the result of the API call. \*
  _ @example
  _ const result = await cart.replaceDeliveryAddresses([
- {
- address: {
- deliveryAddress: {
- address1: '123 Main St',
- city: 'Anytown',
- countryCode: 'US'
- }
- },
- selected: true
- }
- ], { someOptionalParam: 'value' });
  \*/
  replaceDeliveryAddresses: ReturnType<typeof cartDeliveryAddressesReplaceDefault>;
  };
  type HydrogenCartCustom<TCustomMethods extends Partial<HydrogenCart> & CustomMethodsBase> = Omit<HydrogenCart, keyof TCustomMethods> & TCustomMethods;
  declare function createCartHandler(options: CartHandlerOptions): HydrogenCart;
  declare function createCartHandler<TCustomMethods extends CustomMethodsBase>(options: CartHandlerOptionsWithCustom<TCustomMethods>): HydrogenCartCustom<TCustomMethods>;

type RequestEventPayload = {
\_\_fromVite?: boolean;
url: string;
eventType: 'request' | 'subrequest';
requestId?: string | null;
purpose?: string | null;
startTime: number;
endTime?: number;
cacheStatus?: 'MISS' | 'HIT' | 'STALE' | 'PUT';
waitUntil?: WaitUntil;
graphql?: string | null;
stackInfo?: {
file?: string;
func?: string;
line?: number;
column?: number;
};
responsePayload?: any;
responseInit?: Omit<ResponseInit, 'headers'> & {
headers?: [string, string][];
};
cache?: {
status?: string;
strategy?: string;
key?: string | readonly unknown[];
};
displayName?: string;
};

declare const CUSTOMER_ACCOUNT_SESSION_KEY = "customerAccount";
declare const BUYER_SESSION_KEY = "buyer";

interface HydrogenSessionData {
[CUSTOMER_ACCOUNT_SESSION_KEY]: {
accessToken?: string;
expiresAt?: string;
refreshToken?: string;
codeVerifier?: string;
idToken?: string;
nonce?: string;
state?: string;
redirectPath?: string;
};
// for B2B buyer context
[BUYER_SESSION_KEY]: Partial<BuyerInput>;
}

interface HydrogenSession<
Data = SessionData,
FlashData = FlashSessionData,

> {
> get: Session<HydrogenSessionData & Data, FlashData>['get'];
> set: Session<HydrogenSessionData & Data, FlashData>['set'];
> unset: Session<HydrogenSessionData & Data, FlashData>['unset'];
> commit: () => ReturnType<

    SessionStorage<HydrogenSessionData & Data, FlashData>['commitSession']

> ;
> destroy?: () => ReturnType<

    SessionStorage<HydrogenSessionData & Data, FlashData>['destroySession']

> ;
> isPending?: boolean;
> }

type WaitUntil = (promise: Promise<unknown>) => void;

interface HydrogenEnv {
SESSION_SECRET: string;
PUBLIC_STOREFRONT_API_TOKEN: string;
PRIVATE_STOREFRONT_API_TOKEN: string;
PUBLIC_STORE_DOMAIN: string;
PUBLIC_STOREFRONT_ID: string;
PUBLIC_CUSTOMER_ACCOUNT_API_CLIENT_ID: string;
PUBLIC_CUSTOMER_ACCOUNT_API_URL: string;
PUBLIC_CHECKOUT_DOMAIN: string;
SHOP_ID: string;
}

type StorefrontHeaders = {
/** A unique ID that correlates all sub-requests together. \*/
requestGroupId: string | null;
/** The IP address of the client. _/
buyerIp: string | null;
/\*\* The signature of the client's IP address for verification. _/
buyerIpSig: string | null;
/** The cookie header from the client \*/
cookie: string | null;
/** The sec-purpose or purpose header value \*/
purpose: string | null;
};

interface HydrogenRouterContextProvider<
TSession extends HydrogenSession = HydrogenSession,
TCustomMethods extends CustomMethodsBase | undefined = {},
TI18n extends I18nBase = I18nBase,
TEnv extends HydrogenEnv = Env,

> extends RouterContextProvider {
> /** A GraphQL client for querying the Storefront API \*/
> storefront: Storefront<TI18n>;
> /** A GraphQL client for querying the Customer Account API _/
> customerAccount: CustomerAccount;
> /\*\* A collection of utilities used to interact with the cart _/
> cart: TCustomMethods extends CustomMethodsBase

    ? HydrogenCartCustom<TCustomMethods>
    : HydrogenCart;

/** Environment variables from the fetch function \*/
env: TEnv;
/** The waitUntil function for keeping requests alive _/
waitUntil?: WaitUntil;
/\*\* Session implementation _/
session: TSession;
}

declare global {
interface Window {
privacyBanner: PrivacyBanner;
Shopify: {
customerPrivacy: CustomerPrivacy;
};
}
interface Document {
addEventListener<K extends keyof CustomEventMap>(
type: K,
listener: (this: Document, ev: CustomEventMap[K]) => void,
): void;
removeEventListener<K extends keyof CustomEventMap>(
type: K,
listener: (this: Document, ev: CustomEventMap[K]) => void,
): void;
dispatchEvent<K extends keyof CustomEventMap>(ev: CustomEventMap[K]): void;
}
var **H2O_LOG_EVENT: undefined | ((event: RequestEventPayload) => void);
var **remix_devServerHooks:
| undefined
| {getCriticalCss: (...args: unknown[]) => any};
}

type I18nBase = {
language: LanguageCode$1 | LanguageCode;
country: CountryCode$1;
};
type JsonGraphQLError = ReturnType<GraphQLError['toJSON']>;
type StorefrontApiErrors = JsonGraphQLError[] | undefined;
type StorefrontError = {
errors?: StorefrontApiErrors;
};
/\*\*

- Wraps all the returned utilities from `createStorefrontClient`.
  \*/
  type StorefrontClient<TI18n extends I18nBase> = {
  storefront: Storefront<TI18n>;
  };
  /\*\*
- Maps all the queries found in the project to variables and return types.
  \*/
  interface StorefrontQueries {
  }
  /\*\*
- Maps all the mutations found in the project to variables and return types.
  \*/
  interface StorefrontMutations {
  }
  type AutoAddedVariableNames = 'country' | 'language';
  type StorefrontCommonExtraParams = {
  headers?: HeadersInit;
  storefrontApiVersion?: string;
  displayName?: string;
  };
  /\*\*
- Interface to interact with the Storefront API.
  _/
  type Storefront<TI18n extends I18nBase = I18nBase> = {
  query: <OverrideReturnType extends any = never, RawGqlString extends string = string>(query: RawGqlString, ...options: ClientVariablesInRestParams<StorefrontQueries, RawGqlString, StorefrontCommonExtraParams & Pick<StorefrontQueryOptions, 'cache'>, AutoAddedVariableNames>) => Promise<ClientReturn<StorefrontQueries, RawGqlString, OverrideReturnType> & StorefrontError>;
  mutate: <OverrideReturnType extends any = never, RawGqlString extends string = string>(mutation: RawGqlString, ...options: ClientVariablesInRestParams<StorefrontMutations, RawGqlString, StorefrontCommonExtraParams, AutoAddedVariableNames>) => Promise<ClientReturn<StorefrontMutations, RawGqlString, OverrideReturnType> & StorefrontError>;
  cache?: Cache;
  CacheNone: typeof CacheNone;
  CacheLong: typeof CacheLong;
  CacheShort: typeof CacheShort;
  CacheCustom: typeof CacheCustom;
  generateCacheControlHeader: typeof generateCacheControlHeader;
  getPublicTokenHeaders: ReturnType<typeof createStorefrontClient$1>['getPublicTokenHeaders'];
  getPrivateTokenHeaders: ReturnType<typeof createStorefrontClient$1>['getPrivateTokenHeaders'];
  getShopifyDomain: ReturnType<typeof createStorefrontClient$1>['getShopifyDomain'];
  getApiUrl: ReturnType<typeof createStorefrontClient$1>['getStorefrontApiUrl'];
  i18n: TI18n;
  getHeaders: () => Record<string, string>;
  /\*\*
  _ Checks if the request URL matches the Storefront API GraphQL endpoint.
  _/
  isStorefrontApiUrl: (request: {
  url?: string;
  }) => boolean;
  /\*\*
  _ Forwards the request to the Storefront API.
  _ It reads the API version from the request URL.
  _/
  forward: (request: Request, options?: Pick<StorefrontCommonExtraParams, 'storefrontApiVersion'>) => Promise<Response>;
  /**
  _ Sets the collected subrequest headers in the response.
  _ Useful to forward the cookies and server-timing headers
  _ from server subrequests to the browser.
  _/
  setCollectedSubrequestHeaders: (response: {
  headers: Headers;
  }) => void;
  };
  type HydrogenClientProps<TI18n> = {
  /** Storefront API headers. If on Oxygen, use `getStorefrontHeaders()` _/
  storefrontHeaders?: StorefrontHeaders;
  /\*\* An instance that implements the [Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache) _/
  cache?: Cache;
  /** The globally unique identifier for the Shop \*/
  storefrontId?: string;
  /** The `waitUntil` function is used to keep the current request/response lifecycle alive even after a response has been sent. It should be provided by your platform. _/
  waitUntil?: WaitUntil;
  /\*\* An object containing a country code and language code _/
  i18n?: TI18n;
  /** Whether it should print GraphQL errors automatically. Defaults to true \*/
  logErrors?: boolean | ((error?: Error) => boolean);
  };
  type CreateStorefrontClientOptions<TI18n extends I18nBase> = HydrogenClientProps<TI18n> & StorefrontClientProps;
  type StorefrontQueryOptions = StorefrontCommonExtraParams & {
  query: string;
  mutation?: never;
  cache?: CachingStrategy;
  };
  /**
- This function extends `createStorefrontClient` from [Hydrogen React](/docs/api/hydrogen-react/2026-01/utilities/createstorefrontclient). The additional arguments enable internationalization (i18n), caching, and other features particular to Remix and Oxygen.
-
- Learn more about [data fetching in Hydrogen](/docs/custom-storefronts/hydrogen/data-fetching/fetch-data).
  _/
  declare function createStorefrontClient<TI18n extends I18nBase>(options: CreateStorefrontClientOptions<TI18n>): StorefrontClient<TI18n>;
  declare function formatAPIResult<T>(data: T, errors: StorefrontApiErrors): T & StorefrontError;
  type CreateStorefrontClientForDocs<TI18n extends I18nBase> = {
  storefront?: StorefrontForDoc<TI18n>;
  };
  type StorefrontForDoc<TI18n extends I18nBase = I18nBase> = {
  /\*\* The function to run a query on Storefront API. _/
  query?: <TData = any>(query: string, options: StorefrontQueryOptionsForDocs) => Promise<TData & StorefrontError>;
  /** The function to run a mutation on Storefront API. \*/
  mutate?: <TData = any>(mutation: string, options: StorefrontMutationOptionsForDocs) => Promise<TData & StorefrontError>;
  /** The cache instance passed in from the `createStorefrontClient` argument. _/
  cache?: Cache;
  /\*\* Re-export of [`CacheNone`](/docs/api/hydrogen/utilities/cachenone). _/
  CacheNone?: typeof CacheNone;
  /** Re-export of [`CacheLong`](/docs/api/hydrogen/utilities/cachelong). \*/
  CacheLong?: typeof CacheLong;
  /** Re-export of [`CacheShort`](/docs/api/hydrogen/utilities/cacheshort). _/
  CacheShort?: typeof CacheShort;
  /\*\* Re-export of [`CacheCustom`](/docs/api/hydrogen/utilities/cachecustom). _/
  CacheCustom?: typeof CacheCustom;
  /** Re-export of [`generateCacheControlHeader`](/docs/api/hydrogen/utilities/generatecachecontrolheader). \*/
  generateCacheControlHeader?: typeof generateCacheControlHeader;
  /** Returns an object that contains headers that are needed for each query to Storefront API GraphQL endpoint. See [`getPublicTokenHeaders` in Hydrogen React](/docs/api/hydrogen-react/2026-01/utilities/createstorefrontclient#:~:text=%27graphql%27.-,getPublicTokenHeaders,-(props%3F%3A) for more details. _/
  getPublicTokenHeaders?: ReturnType<typeof createStorefrontClient$1>['getPublicTokenHeaders'];
  /\*\* Returns an object that contains headers that are needed for each query to Storefront API GraphQL endpoint for API calls made from a server. See [`getPrivateTokenHeaders` in Hydrogen React](/docs/api/hydrogen-react/2026-01/utilities/createstorefrontclient#:~:text=storefrontApiVersion-,getPrivateTokenHeaders,-(props%3F%3A) for more details._/
  getPrivateTokenHeaders?: ReturnType<typeof createStorefrontClient$1>['getPrivateTokenHeaders'];
  /** Creates the fully-qualified URL to your myshopify.com domain. See [`getShopifyDomain` in Hydrogen React](/docs/api/hydrogen-react/2026-01/utilities/createstorefrontclient#:~:text=StorefrontClientReturn-,getShopifyDomain,-(props%3F%3A) for more details. \*/
  getShopifyDomain?: ReturnType<typeof createStorefrontClient$1>['getShopifyDomain'];
  /** Creates the fully-qualified URL to your store's GraphQL endpoint. See [`getStorefrontApiUrl` in Hydrogen React](/docs/api/hydrogen-react/2026-01/utilities/createstorefrontclient#:~:text=storeDomain-,getStorefrontApiUrl,-(props%3F%3A) for more details._/
  getApiUrl?: ReturnType<typeof createStorefrontClient$1>['getStorefrontApiUrl'];
  /\*\* The `i18n` object passed in from the `createStorefrontClient` argument. _/
  i18n?: TI18n;
  };
  type StorefrontQueryOptionsForDocs = {
  /** The variables for the GraphQL query statement. \*/
  variables?: Record<string, unknown>;
  /** The cache strategy for this query. Default to max-age=1, stale-while-revalidate=86399. _/
  cache?: CachingStrategy;
  /\*\* Additional headers for this query. _/
  headers?: HeadersInit;
  /** Override the Storefront API version for this query. \*/
  storefrontApiVersion?: string;
  /** The name of the query for debugging in the Subrequest Profiler. _/
  displayName?: string;
  };
  type StorefrontMutationOptionsForDocs = {
  /\*\* The variables for the GraphQL mutation statement. _/
  variables?: Record<string, unknown>;
  /** Additional headers for this query. \*/
  headers?: HeadersInit;
  /** Override the Storefront API version for this query. _/
  storefrontApiVersion?: string;
  /\*\* The name of the query for debugging in the Subrequest Profiler. _/
  displayName?: string;
  };

type CartOptionalInput = {
/**
_ The cart id.
_ @default cart.getCartId();
\*/
cartId?: Scalars['ID']['input'];
/**
_ The country code.
_ @default storefront.i18n.country
_/
country?: CountryCode$1;
/\*\*
_ The language code.
_ @default storefront.i18n.language
_/
language?: LanguageCode$1;
/\*\*

- Visitor consent preferences for the Storefront API's @inContext directive.
- \* **Most Hydrogen storefronts do NOT need this.** If you're using Hydrogen's
  _ analytics provider or Shopify's Customer Privacy API (including third-party
  _ consent services integrated with it), consent is handled automatically. \*
  _ This option exists for Storefront API parity and is primarily intended for
  _ non-Hydrogen integrations like Checkout Kit that manage consent outside
  _ Shopify's standard consent flow.
  _
  _ When provided, consent is encoded into the cart's checkoutUrl via the \_cs parameter.
  _ @see https://shopify.dev/docs/storefronts/headless/building-with-the-storefront-api/in-context
  \*/
  visitorConsent?: VisitorConsent$1;
  };
  type MetafieldWithoutOwnerId = Omit<CartMetafieldsSetInput, 'ownerId'>;
  type CartQueryOptions = {
  /**
  _ The storefront client instance created by [`createStorefrontClient`](docs/api/hydrogen/latest/utilities/createstorefrontclient).
  _/
  storefront: Storefront;
  /**
  _ A function that returns the cart ID.
  _/
  getCartId: () => string | undefined;
  /\*\*
  _ The cart fragment to override the one used in this query.
  _/
  cartFragment?: string;
  /\*\*
  _ The customer account instance created by [`createCustomerAccount`](docs/api/hydrogen/latest/customer/createcustomeraccount).
  _/
  customerAccount?: CustomerAccount;
  };
  type CartReturn = Cart & {
  errors?: StorefrontApiErrors;
  };
  type CartQueryData = {
  cart: Cart;
  userErrors?: CartUserError[] | MetafieldsSetUserError[] | MetafieldDeleteUserError[];
  warnings?: CartWarning[];
  };
  type CartQueryDataReturn = CartQueryData & {
  errors?: StorefrontApiErrors;
  };
  type CartQueryReturn<T> = (requiredParams: T, optionalParams?: CartOptionalInput) => Promise<CartQueryData>;

declare const AnalyticsEvent: {
PAGE*VIEWED: "page_viewed";
PRODUCT_VIEWED: "product_viewed";
COLLECTION_VIEWED: "collection_viewed";
CART_VIEWED: "cart_viewed";
SEARCH_VIEWED: "search_viewed";
CART_UPDATED: "cart_updated";
PRODUCT_ADD_TO_CART: "product_added_to_cart";
PRODUCT_REMOVED_FROM_CART: "product_removed_from_cart";
CUSTOM_EVENT: `custom*${string}`;
};

type OtherData = {
/** Any other data that should be included in the event. \*/
[key: string]: unknown;
};
type BasePayload = {
/** The shop data passed in from the `AnalyticsProvider`. _/
shop: ShopAnalytics | null;
/\*\* The custom data passed in from the `AnalyticsProvider`. _/
customData?: AnalyticsProviderProps['customData'];
};
type UrlPayload = {
/** The url location of when this event is collected. \*/
url: string;
};
type ProductPayload = {
/** The product id. _/
id: Product['id'];
/\*\* The product title. _/
title: Product['title'];
/** The displaying variant price. \*/
price: ProductVariant['price']['amount'];
/** The product vendor. _/
vendor: Product['vendor'];
/\*\* The displaying variant id. _/
variantId: ProductVariant['id'];
/** The displaying variant title. \*/
variantTitle: ProductVariant['title'];
/** The quantity of product. _/
quantity: number;
/\*\* The product sku. _/
sku?: ProductVariant['sku'];
/** The product type. \*/
productType?: Product['productType'];
};
type ProductsPayload = {
/** The products associated with this event. _/
products: Array<ProductPayload & OtherData>;
};
type CollectionPayloadDetails = {
/\*\* The collection id. _/
id: string;
/** The collection handle. \*/
handle: string;
};
type CollectionPayload = {
collection: CollectionPayloadDetails;
};
type SearchPayload = {
/** The search term used for the search results page _/
searchTerm: string;
/\*\* The search results _/
searchResults?: any;
};
type CartPayload = {
/** The current cart state. \*/
cart: CartReturn | null;
/** The previous cart state. _/
prevCart: CartReturn | null;
};
type CartLinePayload = {
/\*\* The previous state of the cart line that got updated. _/
prevLine?: CartLine | ComponentizableCartLine;
/\*_ The current state of the cart line that got updated. _/
currentLine?: CartLine | ComponentizableCartLine;
};
type CollectionViewPayload = CollectionPayload & UrlPayload & BasePayload;
type ProductViewPayload = ProductsPayload & UrlPayload & BasePayload;
type CartViewPayload = CartPayload & UrlPayload & BasePayload;
type PageViewPayload = UrlPayload & BasePayload;
type SearchViewPayload = SearchPayload & UrlPayload & BasePayload;
type CartUpdatePayload = CartPayload & BasePayload & OtherData;
type CartLineUpdatePayload = CartLinePayload & CartPayload & BasePayload & OtherData;
type CustomEventPayload = BasePayload & OtherData;
type BasicViewProps = {
data?: OtherData;
customData?: OtherData;
};
type ProductViewProps = {
data: ProductsPayload;
customData?: OtherData;
};
type CollectionViewProps = {
data: CollectionPayload;
customData?: OtherData;
};
type SearchViewProps = {
data?: SearchPayload;
customData?: OtherData;
};
type CustomViewProps = {
type: typeof AnalyticsEvent.CUSTOM_EVENT;
data?: OtherData;
customData?: OtherData;
};
declare function AnalyticsProductView(props: ProductViewProps): react_jsx_runtime.JSX.Element;
declare function AnalyticsCollectionView(props: CollectionViewProps): react_jsx_runtime.JSX.Element;
declare function AnalyticsCartView(props: BasicViewProps): react_jsx_runtime.JSX.Element;
declare function AnalyticsSearchView(props: SearchViewProps): react_jsx_runtime.JSX.Element;
declare function AnalyticsCustomView(props: CustomViewProps): react_jsx_runtime.JSX.Element;

type ConsentStatus = boolean | undefined;
type VisitorConsent = {
marketing: ConsentStatus;
analytics: ConsentStatus;
preferences: ConsentStatus;
sale*of_data: ConsentStatus;
};
type VisitorConsentCollected = {
analyticsAllowed: boolean;
firstPartyMarketingAllowed: boolean;
marketingAllowed: boolean;
preferencesAllowed: boolean;
saleOfDataAllowed: boolean;
thirdPartyMarketingAllowed: boolean;
};
type CustomerPrivacyApiLoaded = boolean;
type CustomerPrivacyConsentConfig = {
checkoutRootDomain: string;
storefrontRootDomain?: string;
storefrontAccessToken: string;
country?: CountryCode$1;
/** The privacyBanner refers to `language` as `locale` \*/
locale?: LanguageCode$1;
};
type SetConsentHeadlessParams = VisitorConsent & CustomerPrivacyConsentConfig & {
headlessStorefront?: boolean;
};
/**
Ideally this type should come from the Custoemr Privacy API sdk
analyticsProcessingAllowed -
currentVisitorConsent
doesMerchantSupportGranularConsent
firstPartyMarketingAllowed
getCCPAConsent
getTrackingConsent
marketingAllowed
preferencesProcessingAllowed
saleOfDataAllowed
saleOfDataRegion
setTrackingConsent
shouldShowBanner
shouldShowGDPRBanner
thirdPartyMarketingAllowed
**/
type OriginalCustomerPrivacy = {
currentVisitorConsent: () => VisitorConsent;
preferencesProcessingAllowed: () => boolean;
saleOfDataAllowed: () => boolean;
marketingAllowed: () => boolean;
analyticsProcessingAllowed: () => boolean;
setTrackingConsent: (consent: SetConsentHeadlessParams, callback: (data: {
error: string;
} | undefined) => void) => void;
shouldShowBanner: () => boolean;
};
type CustomerPrivacy$1 = Omit<OriginalCustomerPrivacy, 'setTrackingConsent'> & {
setTrackingConsent: (consent: VisitorConsent, // we have already applied the headlessStorefront in the override
callback: (data: {
error: string;
} | undefined) => void) => void;
};
type PrivacyBanner$1 = {
loadBanner: (options?: Partial<CustomerPrivacyConsentConfig>) => void;
showPreferences: (options?: Partial<CustomerPrivacyConsentConfig>) => void;
};
interface CustomEventMap$1 {
visitorConsentCollected: CustomEvent<VisitorConsentCollected>;
customerPrivacyApiLoaded: CustomEvent<CustomerPrivacyApiLoaded>;
}
type CustomerPrivacyApiProps = {
/** The production shop checkout domain url. */
checkoutDomain: string;
/\*\* The storefront access token for the shop. _/
storefrontAccessToken: string;
/** Whether to load the Shopify privacy banner as configured in Shopify admin. Defaults to true. \*/
withPrivacyBanner?: boolean;
/** Country code for the shop. _/
country?: CountryCode$1;
/\*\* Language code for the shop. _/
locale?: LanguageCode$1;
/** Callback to be called when visitor consent is collected. \*/
onVisitorConsentCollected?: (consent: VisitorConsentCollected) => void;
/** Callback to be call when customer privacy api is ready. _/
onReady?: () => void;
/\*\*
_ Whether consent libraries can use same-domain requests to the Storefront API.
_ Defaults to true if the standard route proxy is enabled in Hydrogen server.
\_/
sameDomainForStorefrontApi?: boolean;
};
declare function useCustomerPrivacy(props: CustomerPrivacyApiProps): {
customerPrivacy: CustomerPrivacy$1 | null;
privacyBanner?: PrivacyBanner$1 | null;
};

type ShopAnalytics = {
/** The shop ID. \*/
shopId: string;
/** The language code that is being displayed to user. _/
acceptedLanguage: LanguageCode$1;
/\*\* The currency code that is being displayed to user. _/
currency: CurrencyCode;
/** The Hydrogen subchannel ID generated by Oxygen in the environment variable. \*/
hydrogenSubchannelId: string | '0';
};
type Consent = Partial<Pick<CustomerPrivacyApiProps, 'checkoutDomain' | 'sameDomainForStorefrontApi' | 'storefrontAccessToken' | 'withPrivacyBanner' | 'country'>> & {
language?: LanguageCode$1;
};
type AnalyticsProviderProps = {
/** React children to render. _/
children?: ReactNode;
/\*\* The cart or cart promise to track for cart analytics. When there is a difference between the state of the cart, `AnalyticsProvider` will trigger a `cart_updated` event. It will also produce `product_added_to_cart` and `product_removed_from_cart` based on cart line quantity and cart line id changes. _/
cart: Promise<CartReturn | null> | CartReturn | null;
/** An optional function to set wether the user can be tracked. Defaults to Customer Privacy API's `window.Shopify.customerPrivacy.analyticsProcessingAllowed()`. \*/
canTrack?: () => boolean;
/** An optional custom payload to pass to all events. e.g language/locale/currency. _/
customData?: Record<string, unknown>;
/\*\* The shop configuration required to publish analytics events to Shopify. Use [`getShopAnalytics`](/docs/api/hydrogen/utilities/getshopanalytics). _/
shop: Promise<ShopAnalytics | null> | ShopAnalytics | null;
/** The customer privacy consent configuration and options. \*/
consent: Consent;
/** @deprecated Disable throwing errors when required props are missing. _/
disableThrowOnError?: boolean;
/** The domain scope of the cookie set with `useShopifyCookies`. **/
cookieDomain?: string;
};
type AnalyticsContextValue = {
/\*\* A function to tell you the current state of if the user can be tracked by analytics. Defaults to Customer Privacy API's `window.Shopify.customerPrivacy.analyticsProcessingAllowed()`. _/
canTrack: NonNullable<AnalyticsProviderProps['canTrack']>;
/** The current cart state. \*/
cart: Awaited<AnalyticsProviderProps['cart']>;
/** The custom data passed in from the `AnalyticsProvider`. _/
customData?: AnalyticsProviderProps['customData'];
/\*\* The previous cart state. _/
prevCart: Awaited<AnalyticsProviderProps['cart']>;
/** A function to publish an analytics event. \*/
publish: typeof publish;
/** A function to register with the analytics provider. _/
register: (key: string) => {
ready: () => void;
};
/\*\* The shop configuration required to publish events to Shopify. _/
shop: Awaited<AnalyticsProviderProps['shop']>;
/** A function to subscribe to analytics events. \*/
subscribe: typeof subscribe;
/** The privacy banner SDK methods with the config applied _/
privacyBanner: PrivacyBanner$1 | null;
/\*\* The customer privacy SDK methods with the config applied _/
customerPrivacy: CustomerPrivacy$1 | null;
};
declare function subscribe(event: typeof AnalyticsEvent.PAGE\*VIEWED, callback: (payload: PageViewPayload) => void): void;
declare function subscribe(event: typeof AnalyticsEvent.PRODUCT_VIEWED, callback: (payload: ProductViewPayload) => void): void;
declare function subscribe(event: typeof AnalyticsEvent.COLLECTION_VIEWED, callback: (payload: CollectionViewPayload) => void): void;
declare function subscribe(event: typeof AnalyticsEvent.CART_VIEWED, callback: (payload: CartViewPayload) => void): void;
declare function subscribe(event: typeof AnalyticsEvent.SEARCH_VIEWED, callback: (payload: SearchViewPayload) => void): void;
declare function subscribe(event: typeof AnalyticsEvent.CART_UPDATED, callback: (payload: CartUpdatePayload) => void): void;
declare function subscribe(event: typeof AnalyticsEvent.PRODUCT_ADD_TO_CART, callback: (payload: CartLineUpdatePayload) => void): void;
declare function subscribe(event: typeof AnalyticsEvent.PRODUCT_REMOVED_FROM_CART, callback: (payload: CartLineUpdatePayload) => void): void;
declare function subscribe(event: typeof AnalyticsEvent.CUSTOM_EVENT, callback: (payload: CustomEventPayload) => void): void;
declare function publish(event: typeof AnalyticsEvent.PAGE_VIEWED, payload: PageViewPayload): void;
declare function publish(event: typeof AnalyticsEvent.PRODUCT_VIEWED, payload: ProductViewPayload): void;
declare function publish(event: typeof AnalyticsEvent.COLLECTION_VIEWED, payload: CollectionViewPayload): void;
declare function publish(event: typeof AnalyticsEvent.CART_VIEWED, payload: CartViewPayload): void;
declare function publish(event: typeof AnalyticsEvent.CART_UPDATED, payload: CartUpdatePayload): void;
declare function publish(event: typeof AnalyticsEvent.PRODUCT_ADD_TO_CART, payload: CartLineUpdatePayload): void;
declare function publish(event: typeof AnalyticsEvent.PRODUCT_REMOVED_FROM_CART, payload: CartLineUpdatePayload): void;
declare function publish(event: typeof AnalyticsEvent.CUSTOM_EVENT, payload: OtherData): void;
declare function AnalyticsProvider({ canTrack: customCanTrack, cart: currentCart, children, consent, customData, shop: shopProp, cookieDomain, }: AnalyticsProviderProps): JSX.Element;
declare function useAnalytics(): AnalyticsContextValue;
type ShopAnalyticsProps = {
/\*\*

- The storefront client instance created by [`createStorefrontClient`](docs/api/hydrogen/utilities/createstorefrontclient).
  _/
  storefront: Storefront;
  /\*\*
  _ The `PUBLIC_STOREFRONT_ID` generated by Oxygen in the environment variable.
  \_/
  publicStorefrontId: string;
  };
  declare function getShopAnalytics({ storefront, publicStorefrontId, }: ShopAnalyticsProps): Promise<ShopAnalytics | null>;
  declare const Analytics: {
  CartView: typeof AnalyticsCartView;
  CollectionView: typeof AnalyticsCollectionView;
  CustomView: typeof AnalyticsCustomView;
  ProductView: typeof AnalyticsProductView;
  Provider: typeof AnalyticsProvider;
  SearchView: typeof AnalyticsSearchView;
  };

/\*\*

- The cache key is used to uniquely identify a value in the cache.
  \*/
  type CacheKey = string | readonly unknown[];
  type AddDebugDataParam = {
  displayName?: string;
  response?: Pick<Response, 'url' | 'status' | 'statusText' | 'headers'>;
  };
  type CacheActionFunctionParam = {
  addDebugData: (info: AddDebugDataParam) => void;
  };

type CreateWithCacheOptions = {
/** An instance that implements the [Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache) \*/
cache: Cache;
/** The `waitUntil` function is used to keep the current request/response lifecycle alive even after a response has been sent. It should be provided by your platform. _/
waitUntil: WaitUntil;
/\*\* The `request` object is used by the Subrequest profiler, and to access certain headers for debugging _/
request: CrossRuntimeRequest;
};
type WithCacheRunOptions<T> = {
/** The cache key for this run \*/
cacheKey: CacheKey;
/**
_ Use the `CachingStrategy` to define a custom caching mechanism for your data.
_ Or use one of the pre-defined caching strategies: [`CacheNone`](/docs/api/hydrogen/utilities/cachenone), [`CacheShort`](/docs/api/hydrogen/utilities/cacheshort), [`CacheLong`](/docs/api/hydrogen/utilities/cachelong).
_/
cacheStrategy: CachingStrategy;
/\*\* Useful to avoid accidentally caching bad results _/
shouldCacheResult: (value: T) => boolean;
};
type WithCacheFetchOptions<T> = {
displayName?: string;
/**
_ Use the `CachingStrategy` to define a custom caching mechanism for your data.
_ Or use one of the pre-defined caching strategies: [`CacheNone`](/docs/api/hydrogen/utilities/cachenone), [`CacheShort`](/docs/api/hydrogen/utilities/cacheshort), [`CacheLong`](/docs/api/hydrogen/utilities/cachelong).
\*/
cacheStrategy?: CachingStrategy;
/** The cache key for this fetch _/
cacheKey?: CacheKey;
/\*\* Useful to avoid e.g. caching a successful response that contains an error in the body _/
shouldCacheResponse: (body: T, response: Response) => boolean;
};
type WithCache = {
run: <T>(options: WithCacheRunOptions<T>, fn: ({ addDebugData }: CacheActionFunctionParam) => T | Promise<T>) => Promise<T>;
fetch: <T>(url: string, requestInit: RequestInit, options: WithCacheFetchOptions<T>) => Promise<{
data: T | null;
response: Response;
}>;
};
declare function createWithCache(cacheOptions: CreateWithCacheOptions): WithCache;

/\*\*

- This is a limited implementation of an in-memory cache.
- It only supports the `cache-control` header.
- It does NOT support `age` or `expires` headers.
- @see https://developer.mozilla.org/en-US/docs/Web/API/Cache
  \*/
  declare class InMemoryCache implements Cache {
  #private;
  constructor();
  add(request: RequestInfo): Promise<void>;
  addAll(requests: RequestInfo[]): Promise<void>;
  matchAll(request?: RequestInfo, options?: CacheQueryOptions): Promise<readonly Response[]>;
  put(request: Request, response: Response): Promise<void>;
  match(request: Request): Promise<Response | undefined>;
  delete(request: Request): Promise<boolean>;
  keys(request?: Request): Promise<Request[]>;
  }

type OtherFormData = {
[key: string]: unknown;
};
type CartAttributesUpdateProps = {
action: 'AttributesUpdateInput';
inputs?: {
attributes: AttributeInput[];
} & OtherFormData;
};
type CartAttributesUpdateRequire = {
action: 'AttributesUpdateInput';
inputs: {
attributes: AttributeInput[];
} & OtherFormData;
};
type CartBuyerIdentityUpdateProps = {
action: 'BuyerIdentityUpdate';
inputs?: {
buyerIdentity: CartBuyerIdentityInput;
} & OtherFormData;
};
type CartBuyerIdentityUpdateRequire = {
action: 'BuyerIdentityUpdate';
inputs: {
buyerIdentity: CartBuyerIdentityInput;
} & OtherFormData;
};
type CartCreateProps = {
action: 'Create';
inputs?: {
input: CartInput;
} & OtherFormData;
};
type CartCreateRequire = {
action: 'Create';
inputs: {
input: CartInput;
} & OtherFormData;
};
type CartDiscountCodesUpdateProps = {
action: 'DiscountCodesUpdate';
inputs?: {
discountCodes: string[];
} & OtherFormData;
};
type CartDiscountCodesUpdateRequire = {
action: 'DiscountCodesUpdate';
inputs: {
discountCodes: string[];
} & OtherFormData;
};
type CartGiftCardCodesUpdateProps = {
action: 'GiftCardCodesUpdate';
inputs?: {
giftCardCodes: string[];
} & OtherFormData;
};
type CartGiftCardCodesUpdateRequire = {
action: 'GiftCardCodesUpdate';
inputs: {
giftCardCodes: string[];
} & OtherFormData;
};
type CartGiftCardCodesAddProps = {
action: 'GiftCardCodesAdd';
inputs?: {
giftCardCodes: string[];
} & OtherFormData;
};
type CartGiftCardCodesAddRequire = {
action: 'GiftCardCodesAdd';
inputs: {
giftCardCodes: string[];
} & OtherFormData;
};
type CartGiftCardCodesRemoveProps = {
action: 'GiftCardCodesRemove';
inputs?: {
giftCardCodes: string[];
} & OtherFormData;
};
type CartGiftCardCodesRemoveRequire = {
action: 'GiftCardCodesRemove';
inputs: {
giftCardCodes: string[];
} & OtherFormData;
};
type OptimisticCartLineInput = CartLineInput & {
selectedVariant?: unknown;
};
type CartLinesAddProps = {
action: 'LinesAdd';
inputs?: {
lines: Array<OptimisticCartLineInput>;
} & OtherFormData;
};
type CartLinesAddRequire = {
action: 'LinesAdd';
inputs: {
lines: Array<OptimisticCartLineInput>;
} & OtherFormData;
};
type CartLinesUpdateProps = {
action: 'LinesUpdate';
inputs?: {
lines: CartLineUpdateInput[];
} & OtherFormData;
};
type CartLinesUpdateRequire = {
action: 'LinesUpdate';
inputs: {
lines: CartLineUpdateInput[];
} & OtherFormData;
};
type CartLinesRemoveProps = {
action: 'LinesRemove';
inputs?: {
lineIds: string[];
} & OtherFormData;
};
type CartLinesRemoveRequire = {
action: 'LinesRemove';
inputs: {
lineIds: string[];
} & OtherFormData;
};
type CartNoteUpdateProps = {
action: 'NoteUpdate';
inputs?: {
note: string;
} & OtherFormData;
};
type CartNoteUpdateRequire = {
action: 'NoteUpdate';
inputs: {
note: string;
} & OtherFormData;
};
type CartSelectedDeliveryOptionsUpdateProps = {
action: 'SelectedDeliveryOptionsUpdate';
inputs?: {
selectedDeliveryOptions: CartSelectedDeliveryOptionInput[];
} & OtherFormData;
};
type CartSelectedDeliveryOptionsUpdateRequire = {
action: 'SelectedDeliveryOptionsUpdate';
inputs: {
selectedDeliveryOptions: CartSelectedDeliveryOptionInput[];
} & OtherFormData;
};
type CartMetafieldsSetProps = {
action: 'MetafieldsSet';
inputs?: {
metafields: MetafieldWithoutOwnerId[];
} & OtherFormData;
};
type CartMetafieldsSetRequire = {
action: 'MetafieldsSet';
inputs: {
metafields: MetafieldWithoutOwnerId[];
} & OtherFormData;
};
type CartMetafieldDeleteProps = {
action: 'MetafieldsDelete';
inputs?: {
key: Scalars['String']['input'];
} & OtherFormData;
};
type CartMetafieldDeleteRequire = {
action: 'MetafieldsDelete';
inputs: {
key: Scalars['String']['input'];
} & OtherFormData;
};
type CartDeliveryAddressesAddProps = {
action: 'DeliveryAddressesAdd';
inputs?: {
addresses: Array<CartSelectableAddressInput>;
} & OtherFormData;
};
type CartDeliveryAddressesAddRequire = {
action: 'DeliveryAddressesAdd';
inputs: {
addresses: Array<CartSelectableAddressInput>;
} & OtherFormData;
};
type CartDeliveryAddressesRemoveProps = {
action: 'DeliveryAddressesRemove';
inputs?: {
addressIds: Array<string> | Array<Scalars['ID']['input']>;
} & OtherFormData;
};
type CartDeliveryAddressesRemoveRequire = {
action: 'DeliveryAddressesRemove';
inputs: {
addressIds: Array<string> | Array<Scalars['ID']['input']>;
} & OtherFormData;
};
type CartDeliveryAddressesUpdateProps = {
action: 'DeliveryAddressesUpdate';
inputs?: {
addresses: Array<CartSelectableAddressUpdateInput>;
} & OtherFormData;
};
type CartDeliveryAddressesUpdateRequire = {
action: 'DeliveryAddressesUpdate';
inputs: {
addresses: Array<CartSelectableAddressUpdateInput>;
} & OtherFormData;
};
type CartDeliveryAddressesReplaceProps = {
action: 'DeliveryAddressesReplace';
inputs?: {
addresses: Array<CartSelectableAddressInput>;
} & OtherFormData;
};
type CartDeliveryAddressesReplaceRequire = {
action: 'DeliveryAddressesReplace';
inputs: {
addresses: Array<CartSelectableAddressInput>;
} & OtherFormData;
};
type CartCustomProps = {
action: `Custom${string}`;
inputs?: Record<string, unknown>;
};
type CartCustomRequire = {
action: `Custom${string}`;
inputs: Record<string, unknown>;
};
type CartFormCommonProps = {
/**
_ Children nodes of CartForm.
_ Children can be a render prop that receives the fetcher.
\*/
children: ReactNode | ((fetcher: FetcherWithComponents<any>) => ReactNode);
/**
_ The route to submit the form to. Defaults to the current route.
_/
route?: string;
/\*\*
_ Optional key to use for the fetcher.
_ @see https://remix.run/hooks/use-fetcher#key
\*/
fetcherKey?: string;
};
type CartActionInputProps = CartAttributesUpdateProps | CartBuyerIdentityUpdateProps | CartCreateProps | CartDiscountCodesUpdateProps | CartGiftCardCodesUpdateProps | CartGiftCardCodesAddProps | CartGiftCardCodesRemoveProps | CartLinesAddProps | CartLinesUpdateProps | CartLinesRemoveProps | CartNoteUpdateProps | CartSelectedDeliveryOptionsUpdateProps | CartMetafieldsSetProps | CartMetafieldDeleteProps | CartDeliveryAddressesAddProps | CartDeliveryAddressesRemoveProps | CartDeliveryAddressesUpdateProps | CartDeliveryAddressesReplaceProps | CartCustomProps;
type CartActionInput = CartAttributesUpdateRequire | CartBuyerIdentityUpdateRequire | CartCreateRequire | CartDiscountCodesUpdateRequire | CartGiftCardCodesUpdateRequire | CartGiftCardCodesAddRequire | CartGiftCardCodesRemoveRequire | CartLinesAddRequire | CartLinesUpdateRequire | CartLinesRemoveRequire | CartNoteUpdateRequire | CartSelectedDeliveryOptionsUpdateRequire | CartMetafieldsSetRequire | CartMetafieldDeleteRequire | CartDeliveryAddressesAddRequire | CartDeliveryAddressesRemoveRequire | CartDeliveryAddressesUpdateRequire | CartDeliveryAddressesReplaceRequire | CartCustomRequire;
type CartFormProps = CartActionInputProps & CartFormCommonProps;
declare function CartForm({ children, action, inputs, route, fetcherKey, }: CartFormProps): JSX.Element;
declare namespace CartForm {
var INPUT_NAME: string;
var ACTIONS: {
readonly AttributesUpdateInput: "AttributesUpdateInput";
readonly BuyerIdentityUpdate: "BuyerIdentityUpdate";
readonly Create: "Create";
readonly DiscountCodesUpdate: "DiscountCodesUpdate";
readonly GiftCardCodesUpdate: "GiftCardCodesUpdate";
readonly GiftCardCodesAdd: "GiftCardCodesAdd";
readonly GiftCardCodesRemove: "GiftCardCodesRemove";
readonly LinesAdd: "LinesAdd";
readonly LinesRemove: "LinesRemove";
readonly LinesUpdate: "LinesUpdate";
readonly NoteUpdate: "NoteUpdate";
readonly SelectedDeliveryOptionsUpdate: "SelectedDeliveryOptionsUpdate";
readonly MetafieldsSet: "MetafieldsSet";
readonly MetafieldDelete: "MetafieldDelete";
readonly DeliveryAddressesAdd: "DeliveryAddressesAdd";
readonly DeliveryAddressesUpdate: "DeliveryAddressesUpdate";
readonly DeliveryAddressesRemove: "DeliveryAddressesRemove";
readonly DeliveryAddressesReplace: "DeliveryAddressesReplace";
};
var getFormInput: (formData: FormData) => CartActionInput;
}

declare const cartGetIdDefault: (requestHeaders: CrossRuntimeRequest["headers"]) => () => string | undefined;

type CookieOptions = {
maxage?: number;
expires?: Date | number | string;
samesite?: 'Lax' | 'Strict' | 'None';
secure?: boolean;
httponly?: boolean;
domain?: string;
path?: string;
};
declare const cartSetIdDefault: (cookieOptions?: CookieOptions) => (cartId: string) => Headers;

type LikeACart = {
lines: {
nodes: Array<unknown>;
};
};
type OptimisticCartLine<T = CartLine | CartReturn> = T extends LikeACart ? T['lines']['nodes'][number] & {
isOptimistic?: boolean;
} : T & {
isOptimistic?: boolean;
};
type OptimisticCart<T = CartReturn> = T extends undefined | null ? // This is the null/undefined case, where the cart has yet to be created.
{
isOptimistic?: boolean;
lines: {
nodes: Array<OptimisticCartLine>;
};
totalQuantity?: number;
} & Omit<PartialDeep<CartReturn>, 'lines'> : Omit<T, 'lines'> & {
isOptimistic?: boolean;
lines: {
nodes: Array<OptimisticCartLine<T>>;
};
totalQuantity?: number;
};
/\*\*

- @param cart The cart object from `context.cart.get()` returned by a server loader.
-
- @returns A new cart object augmented with optimistic state for `lines` and `totalQuantity`. Each cart line item that is optimistically added includes an `isOptimistic` property. Also if the cart has _any_ optimistic state, a root property `isOptimistic` will be set to `true`.
  \*/
  declare function useOptimisticCart<DefaultCart = {
  lines?: {
  nodes: Array<{
  id: string;
  quantity: number;
  merchandise: {
  is: string;
  };
  }>;
  };
  }>(cart?: DefaultCart): OptimisticCart<DefaultCart>;

/\*\*

- A custom Remix loader handler that fetches the changelog.json from GitHub.
- It is used by the `upgrade` command inside the route `https://hydrogen.shopify.dev/changelog.json`
  \*/
  declare function changelogHandler({ request, changelogUrl, }: {
  request: Request;
  changelogUrl?: string;
  }): Promise<Response>;

/\*\*

- Grouped export of all Hydrogen context keys for convenient access.
- Use with React Router's context.get() pattern:
-
- @example
- ```ts

  ```

- import { hydrogenContext } from '@shopify/hydrogen';
-
- export async function loader({ context }) {
- const storefront = context.get(hydrogenContext.storefront);
- const cart = context.get(hydrogenContext.cart);
- }
- ```
   */
  declare const hydrogenContext: {
      readonly storefront: react_router.RouterContext<Storefront<I18nBase>>;
      readonly cart: react_router.RouterContext<HydrogenCart | HydrogenCartCustom<CustomMethodsBase>>;
      readonly customerAccount: react_router.RouterContext<CustomerAccount>;
      readonly env: react_router.RouterContext<HydrogenEnv>;
      readonly session: react_router.RouterContext<HydrogenSession<react_router.SessionData, any>>;
      readonly waitUntil: react_router.RouterContext<WaitUntil>;
  };
  ```

type HydrogenContextOptions<TSession extends HydrogenSession = HydrogenSession, TCustomMethods extends CustomMethodsBase | undefined = {}, TI18n extends I18nBase = I18nBase, TEnv extends HydrogenEnv = Env> = {
env: TEnv;
request: CrossRuntimeRequest;
/** An instance that implements the [Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache) \*/
cache?: Cache;
/** The `waitUntil` function is used to keep the current request/response lifecycle alive even after a response has been sent. It should be provided by your platform. _/
waitUntil?: WaitUntil;
/\*\* Any cookie implementation. By default Hydrogen ships with cookie session storage, but you can use [another session storage](https://remix.run/docs/en/main/utils/sessions) implementation. _/
session: TSession;
/** An object containing a country code and language code \*/
i18n?: TI18n;
/** Whether it should print GraphQL errors automatically. Defaults to true _/
logErrors?: boolean | ((error?: Error) => boolean);
/\*\* Storefront client overwrite options. See documentation for createStorefrontClient for more information. _/
storefront?: {
/** Storefront API headers. Default values set from request header. \*/
headers?: CreateStorefrontClientOptions<TI18n>['storefrontHeaders'];
/** Override the Storefront API version for this query. _/
apiVersion?: CreateStorefrontClientOptions<TI18n>['storefrontApiVersion'];
};
/\*\* Customer Account client overwrite options. See documentation for createCustomerAccountClient for more information. _/
customerAccount?: {
/** Override the version of the API \*/
apiVersion?: CustomerAccountOptions['customerApiVersion'];
/** This is the route in your app that authorizes the customer after logging in. Make sure to call `customer.authorize()` within the loader on this route. It defaults to `/account/authorize`. _/
authUrl?: CustomerAccountOptions['authUrl'];
/\*\* Use this method to overwrite the default logged-out redirect behavior. The default handler [throws a redirect](https://remix.run/docs/en/main/utils/redirect#:~:text=!session) to `/account/login` with current path as `return_to` query param. _/
customAuthStatusHandler?: CustomerAccountOptions['customAuthStatusHandler'];
/** Deprecated. `unstableB2b` is now stable. Please remove. \*/
unstableB2b?: CustomerAccountOptions['unstableB2b'];
};
/** Cart handler overwrite options. See documentation for createCartHandler for more information. _/
cart?: {
/\*\* A function that returns the cart id in the form of `gid://shopify/Cart/c1-123`. _/
getId?: CartHandlerOptions['getCartId'];
/** A function that sets the cart ID. \*/
setId?: CartHandlerOptions['setCartId'];
/**
_ The cart query fragment used by `cart.get()`.
_ See the [example usage](/docs/api/hydrogen/utilities/createcarthandler#example-cart-fragments) in the documentation.
_/
queryFragment?: CartHandlerOptions['cartQueryFragment'];
/\*\*
_ The cart mutation fragment used in most mutation requests, except for `setMetafields` and `deleteMetafield`.
_ See the [example usage](/docs/api/hydrogen/utilities/createcarthandler#example-cart-fragments) in the documentation.
_/
mutateFragment?: CartHandlerOptions['cartMutateFragment'];
/**
_ Define custom methods or override existing methods for your cart API instance.
_ See the [example usage](/docs/api/hydrogen/utilities/createcarthandler#example-custom-methods) in the documentation.
\*/
customMethods?: TCustomMethods;
};
buyerIdentity?: CartBuyerIdentityInput;
};
interface HydrogenContext<TSession extends HydrogenSession = HydrogenSession, TCustomMethods extends CustomMethodsBase | undefined = {}, TI18n extends I18nBase = I18nBase, TEnv extends HydrogenEnv = Env> {
/** A GraphQL client for querying the [Storefront API](https://shopify.dev/docs/api/storefront). _/
storefront: StorefrontClient<TI18n>['storefront'];
/\*\* A GraphQL client for querying the [Customer Account API](https://shopify.dev/docs/api/customer). It also provides methods to authenticate and check if the user is logged in. _/
customerAccount: CustomerAccount;
/** A collection of utilities used to interact with the cart. \*/
cart: TCustomMethods extends CustomMethodsBase ? HydrogenCartCustom<TCustomMethods> : HydrogenCart;
env: TEnv;
/** The `waitUntil` function is used to keep the current request/response lifecycle alive even after a response has been sent. It should be provided by your platform. _/
waitUntil?: WaitUntil;
/\*\* Any cookie implementation. By default Hydrogen ships with cookie session storage, but you can use [another session storage](https://remix.run/docs/en/main/utils/sessions) implementation. _/
session: TSession;
}
declare function createHydrogenContext<TSession extends HydrogenSession, TCustomMethods extends CustomMethodsBase | undefined = {}, TI18n extends I18nBase = I18nBase, TEnv extends HydrogenEnv = Env, TAdditionalContext extends Record<string, any> = {}>(options: HydrogenContextOptions<TSession, TCustomMethods, TI18n, TEnv>, additionalContext?: TAdditionalContext): HydrogenRouterContextProvider<TSession, TCustomMethods, TI18n, TEnv> & TAdditionalContext;

type CreateRequestHandlerOptions<Context = unknown> = {
/** React Router's server build \*/
build: ServerBuild;
/** React Router's mode _/
mode?: string;
/\*\*
_ Function to provide the load context for each request.
_ It must contain Hydrogen's storefront client instance
_ for other Hydrogen utilities to work properly.
_/
getLoadContext?: (request: Request) => Promise<Context> | Context;
/\*\*
_ Whether to include the `powered-by` header in responses
_ @default true
_/
poweredByHeader?: boolean;
/**
_ Collect tracking information from subrequests such as cookies
_ and forward them to the browser. Disable this if you are not
_ using Hydrogen's built-in analytics.
_ @default true
\*/
collectTrackingInformation?: boolean;
/**
_ Whether to proxy standard routes such as `/api/.../graphql.json` (Storefront API).
_ You can disable this if you are handling these routes yourself. Ensure that
_ the proxy works if you rely on Hydrogen's built-in behaviors such as analytics.
_ @default true
\*/
proxyStandardRoutes?: boolean;
};
/\*\*

- Creates a request handler for Hydrogen apps using React Router.
  \*/
  declare function createRequestHandler<Context = unknown>({ build, mode, poweredByHeader, getLoadContext, collectTrackingInformation, proxyStandardRoutes, }: CreateRequestHandlerOptions<Context>): (request: Request) => Promise<Response>;

declare const NonceProvider: react.Provider<string | undefined>;
declare const useNonce: () => string | undefined;
type ContentSecurityPolicy = {
/** A randomly generated nonce string that should be passed to any custom `script` element \*/
nonce: string;
/** The content security policy header _/
header: string;
NonceProvider: ComponentType<{
children: ReactNode;
}>;
};
type DirectiveValues = string[] | string | boolean;
type CreateContentSecurityPolicy = {
defaultSrc?: DirectiveValues;
scriptSrc?: DirectiveValues;
scriptSrcElem?: DirectiveValues;
styleSrc?: DirectiveValues;
imgSrc?: DirectiveValues;
connectSrc?: DirectiveValues;
fontSrc?: DirectiveValues;
objectSrc?: DirectiveValues;
mediaSrc?: DirectiveValues;
frameSrc?: DirectiveValues;
sandbox?: DirectiveValues;
reportUri?: DirectiveValues;
childSrc?: DirectiveValues;
formAction?: DirectiveValues;
frameAncestors?: DirectiveValues;
pluginTypes?: DirectiveValues;
baseUri?: DirectiveValues;
reportTo?: DirectiveValues;
workerSrc?: DirectiveValues;
manifestSrc?: DirectiveValues;
prefetchSrc?: DirectiveValues;
navigateTo?: DirectiveValues;
upgradeInsecureRequests?: boolean;
blockAllMixedContent?: boolean;
};
type ShopifyDomains = {
/\*\* The production shop checkout domain url. _/
checkoutDomain?: string;
/** The production shop domain url. \*/
storeDomain?: string;
};
type ShopProp = {
/** Shop specific configurations \*/
shop?: ShopifyDomains;
};
/\*\*

- @param directives - Pass custom [content security policy directives](https://content-security-policy.com/). This is important if you load content in your app from third-party domains.
  \*/
  declare function createContentSecurityPolicy(props?: CreateContentSecurityPolicy & ShopProp): ContentSecurityPolicy;

interface HydrogenScriptProps {
/\*_ Wait to load the script until after the page hydrates. This prevents hydration errors for scripts that modify the DOM. Note: For security, `nonce` is not supported when using `waitForHydration`. Instead you need to add the domain of the script directly to your [Content Securitiy Policy directives](https://shopify.dev/docs/storefronts/headless/hydrogen/content-security-policy#step-3-customize-the-content-security-policy)._/
waitForHydration?: boolean;
}
interface ScriptAttributes extends ScriptHTMLAttributes<HTMLScriptElement> {
}
declare const Script: react.ForwardRefExoticComponent<HydrogenScriptProps & ScriptAttributes & react.RefAttributes<HTMLScriptElement>>;

declare function createCustomerAccountClient({ session, customerAccountId, shopId, customerApiVersion, request, waitUntil, authUrl, customAuthStatusHandler, logErrors, loginPath, authorizePath, defaultRedirectPath, language, }: CustomerAccountOptions): CustomerAccount;

declare function hydrogenRoutes(currentRoutes: Array<RouteConfigEntry>): Promise<Array<RouteConfigEntry>>;

declare function useOptimisticData<T>(identifier: string): T;
type OptimisticInputProps = {
/**
_ A unique identifier for the optimistic input. Use the same identifier in `useOptimisticData`
_ to retrieve the optimistic data from actions.
\*/
id: string;
/**
_ The data to be stored in the optimistic input. Use for creating an optimistic successful state
_ of this form action.
\*/
data: Record<string, unknown>;
};
declare function OptimisticInput({ id, data }: OptimisticInputProps): react_jsx_runtime.JSX.Element;

declare global {
interface Window {
\_\_hydrogenHydrated?: boolean;
}
}
type Connection<NodesType> = {
nodes: Array<NodesType>;
pageInfo: PageInfo;
} | {
edges: Array<{
node: NodesType;
}>;
pageInfo: PageInfo;
};
interface PaginationInfo<NodesType> {
/** The paginated array of nodes. You should map over and render this array. \*/
nodes: Array<NodesType>;
/** The `<NextLink>` is a helper component that makes it easy to navigate to the next page of paginated data. Alternatively you can build your own `<Link>` component: `<Link to={nextPageUrl} state={state} preventScrollReset />` _/
NextLink: ForwardRefExoticComponent<Omit<LinkProps, 'to'> & RefAttributes<HTMLAnchorElement>>;
/\*\* The `<PreviousLink>` is a helper component that makes it easy to navigate to the previous page of paginated data. Alternatively you can build your own `<Link>` component: `<Link to={previousPageUrl} state={state} preventScrollReset />` _/
PreviousLink: ForwardRefExoticComponent<Omit<LinkProps, 'to'> & RefAttributes<HTMLAnchorElement>>;
/** The URL to the previous page of paginated data. Use this prop to build your own `<Link>` component. \*/
previousPageUrl: string;
/** The URL to the next page of paginated data. Use this prop to build your own `<Link>` component. _/
nextPageUrl: string;
/\*\* True if the cursor has next paginated data _/
hasNextPage: boolean;
/** True if the cursor has previous paginated data \*/
hasPreviousPage: boolean;
/** True if we are in the process of fetching another page of data _/
isLoading: boolean;
/\*\* The `state` property is important to use when building your own `<Link>` component if you want paginated data to continuously append to the page. This means that every time the user clicks "Next page", the next page of data will be apppended inline with the previous page. If you want the whole page to re-render with only the next page results, do not pass the `state` prop to the Remix `<Link>` component. _/
state: {
nodes: Array<NodesType>;
pageInfo: {
endCursor: Maybe<string> | undefined;
startCursor: Maybe<string> | undefined;
hasPreviousPage: boolean;
};
};
}
type PaginationProps<NodesType> = {
/** The response from `storefront.query` for a paginated request. Make sure the query is passed pagination variables and that the query has `pageInfo` with `hasPreviousPage`, `hasNextpage`, `startCursor`, and `endCursor` defined. \*/
connection: Connection<NodesType>;
/** A render prop that includes pagination data and helpers. _/
children: PaginationRenderProp<NodesType>;
/\*\* A namespace for the pagination component to avoid URL param conflicts when using multiple `Pagination` components on a single page. _/
namespace?: string;
};
type PaginationRenderProp<NodesType> = FC<PaginationInfo<NodesType>>;
/\*\*

-
- The [Storefront API uses cursors](https://shopify.dev/docs/api/usage/pagination-graphql) to paginate through lists of data
- and the \`<Pagination />\` component makes it easy to paginate data from the Storefront API.
-
- @prop connection The response from `storefront.query` for a paginated request. Make sure the query is passed pagination variables and that the query has `pageInfo` with `hasPreviousPage`, `hasNextpage`, `startCursor`, and `endCursor` defined.
- @prop children A render prop that includes pagination data and helpers.
  \*/
  declare function Pagination<NodesType>({ connection, children, namespace, }: PaginationProps<NodesType>): ReturnType<FC>;
  /\*\*
- @param request The request object passed to your Remix loader function.
- @param options Options for how to configure the pagination variables. Includes the ability to change how many nodes are within each page as well as a namespace to avoid URL param conflicts when using multiple `Pagination` components on a single page.
-
- @returns Variables to be used with the `storefront.query` function
  \*/
  declare function getPaginationVariables(request: Request, options?: {
  pageBy: number;
  namespace?: string;
  }): {
  last: number;
  startCursor: string | null;
  } | {
  first: number;
  endCursor: string | null;
  };

type OptimisticVariant<T> = T & {
isOptimistic?: boolean;
};
type OptimisticVariantInput = PartialDeep<ProductVariant>;
type OptimisticProductVariants = Array<PartialDeep<ProductVariant>> | Promise<Array<PartialDeep<ProductVariant>>> | PartialDeep<ProductVariant> | Promise<PartialDeep<ProductVariant>>;
/\*\*

- @param selectedVariant The `selectedVariant` field queried with `variantBySelectedOptions`.
- @param variants The available product variants for the product. This can be an array of variants, a promise that resolves to an array of variants, or an object with a `product` key that contains the variants.
- @returns A new product object where the `selectedVariant` property is set to the variant that matches the current URL search params. If no variant is found, the original product object is returned. The `isOptimistic` property is set to `true` if the `selectedVariant` has been optimistically changed.
  \*/
  declare function useOptimisticVariant<SelectedVariant = OptimisticVariantInput, Variants = OptimisticProductVariants>(selectedVariant: SelectedVariant, variants: Variants): OptimisticVariant<SelectedVariant>;

type VariantOption = {
name: string;
value?: string;
values: Array<VariantOptionValue>;
};
type PartialProductOptionValues = PartialDeep<ProductOptionValue>;
type PartialProductOption = PartialDeep<Omit<ProductOption, 'optionValues'> & {
optionValues: Array<PartialProductOptionValues>;
}>;
type VariantOptionValue = {
value: string;
isAvailable: boolean;
to: string;
search: string;
isActive: boolean;
variant?: PartialDeep<ProductVariant, {
recurseIntoArrays: true;
}>;
optionValue: PartialProductOptionValues;
};
/\*\*

- @deprecated VariantSelector will be deprecated and removed in the next major version 2025-10
- Please use [getProductOptions](https://shopify.dev/docs/api/hydrogen/latest/utilities/getproductoptions),
- [getSelectedProductOptions](https://shopify.dev/docs/api/hydrogen/latest/utilities/getselectedproductoptions),
- [getAdjacentAndFirstAvailableVariants](https://shopify.dev/docs/api/hydrogen/latest/utilities/getadjacentandfirstavailablevariants) utils instead.
- and [useSelectedOptionInUrlParam](https://shopify.dev/docs/api/hydrogen/latest/utilities/useselectedoptioninurlparam)
- For a full implementation see the Skeleton template [routes/product.$handle.tsx](https://github.com/Shopify/hydrogen/blob/main/templates/skeleton/app/routes/products.%24handle.tsx).
  _/
  type VariantSelectorProps = {
  /\*\* The product handle for all of the variants _/
  handle: string;
  /** Product options from the [Storefront API](/docs/api/storefront/2026-01/objects/ProductOption). Make sure both `name` and `values` are a part of your query. \*/
  options: Array<PartialProductOption> | undefined;
  /** Product variants from the [Storefront API](/docs/api/storefront/2026-01/objects/ProductVariant). You only need to pass this prop if you want to show product availability. If a product option combination is not found within `variants`, it is assumed to be available. Make sure to include `availableForSale` and `selectedOptions.name` and `selectedOptions.value`. _/
  variants?: PartialDeep<ProductVariantConnection> | Array<PartialDeep<ProductVariant>>;
  /\*\* By default all products are under /products. Use this prop to provide a custom path. _/
  productPath?: string;
  /** Should the VariantSelector wait to update until after the browser navigates to a variant. \*/
  waitForNavigation?: boolean;
  /** An optional selected variant to use for the initial state if no URL parameters are set \*/
  selectedVariant?: Maybe<PartialDeep<ProductVariant>>;
  children: ({ option }: {
  option: VariantOption;
  }) => ReactNode;
  };
  /\*\*
- @deprecated VariantSelector will be deprecated and removed in the next major version 2025-10
- Please use [getProductOptions](https://shopify.dev/docs/api/hydrogen/latest/utilities/getproductoptions),
- [getSelectedProductOptions](https://shopify.dev/docs/api/hydrogen/latest/utilities/getselectedproductoptions),
- [getAdjacentAndFirstAvailableVariants](https://shopify.dev/docs/api/hydrogen/latest/utilities/getadjacentandfirstavailablevariants) utils instead.
- and [useSelectedOptionInUrlParam](https://shopify.dev/docs/api/hydrogen/latest/utilities/useselectedoptioninurlparam)
- For a full implementation see the Skeleton template [routes/product.$handle.tsx](https://github.com/Shopify/hydrogen/blob/main/templates/skeleton/app/routes/products.%24handle.tsx).
  \*/
  declare function VariantSelector({ handle, options: \_options, variants: \_variants, productPath, waitForNavigation, selectedVariant, children, }: VariantSelectorProps): react.FunctionComponentElement<{
  children?: ReactNode | undefined;
  }>;
  type GetSelectedProductOptions = (request: Request) => SelectedOptionInput[];
  /\*\*
- Extract searchParams from a Request instance and return an array of selected options.
- @param request - The Request instance to extract searchParams from.
- @returns An array of selected options.
- @example Basic usage:
- ```tsx

  ```

-
- import {getSelectedProductOptions} from '@shopify/hydrogen';
-
- // Given a request url of `/products/product-handle?color=red&size=large`
-
- const selectedOptions = getSelectedProductOptions(request);
-
- // selectedOptions will equal:
- // [
- // {name: 'color', value: 'red'},
- // {name: 'size', value: 'large'}
- // ]
- ```
   **/
  declare const getSelectedProductOptions: GetSelectedProductOptions;
  ```

/\*\*

- Official Hydrogen Preset for React Router 7.12.x
-
- Provides optimal React Router configuration for Hydrogen applications on Oxygen.
- Enables validated performance optimizations while ensuring CLI compatibility.
-
- React Router 7.12.x Feature Support Matrix for Hydrogen 2025.7.0
-
- +----------------------------------+----------+----------------------------------+
- | Feature | Status | Notes |
- +----------------------------------+----------+----------------------------------+
- | CORE CONFIGURATION |
- +----------------------------------+----------+----------------------------------+
- | appDirectory: 'app' | Enabled | Core application structure |
- | buildDirectory: 'dist' | Enabled | Build output configuration |
- | ssr: true | Enabled | Server-side rendering |
- +----------------------------------+----------+----------------------------------+
- | PERFORMANCE FLAGS |
- +----------------------------------+----------+----------------------------------+
- | v8_middleware | Enabled | Required for Hydrogen context |
- | v8_splitRouteModules | Enabled | Route code splitting |
- | unstable_optimizeDeps | Enabled | Build performance optimization |
- +----------------------------------+----------+----------------------------------+
- | ROUTE DISCOVERY |
- +----------------------------------+----------+----------------------------------+
- | routeDiscovery: { mode: 'lazy' } | Default | Lazy route loading |
- | routeDiscovery: { mode: 'init' } | Allowed | Eager route loading |
- +----------------------------------+----------+----------------------------------+
- | UNSUPPORTED FEATURES |
- +----------------------------------+----------+----------------------------------+
- | basename: '/path' | Blocked | CLI infrastructure limitation |
- | prerender: ['/routes'] | Blocked | Plugin incompatibility |
- | serverBundles: () => {} | Blocked | Manifest incompatibility |
- | buildEnd: () => {} | Blocked | CLI bypasses hook execution |
- | unstable_subResourceIntegrity | Blocked | CSP nonce/hash conflict |
- | v8_viteEnvironmentApi | Blocked | CLI fallback detection used |
- +----------------------------------+----------+----------------------------------+
-
- @version 2025.7.0
  \*/
  declare function hydrogenPreset(): Preset;

declare const RichText: typeof RichText$1;

type GraphiQLLoader = (args: LoaderFunctionArgs) => Promise<Response>;
declare const graphiqlLoader: GraphiQLLoader;

type StorefrontRedirect = {
/** The [Storefront client](/docs/api/hydrogen/utilities/createstorefrontclient) instance \*/
storefront: Storefront<I18nBase>;
/** The [MDN Request](https://developer.mozilla.org/en-US/docs/Web/API/Request) object that was passed to the `server.ts` request handler. _/
request: Request;
/\*\* The [MDN Response](https://developer.mozilla.org/en-US/docs/Web/API/Response) object created by `handleRequest` _/
response?: Response;
/** By default the `/admin` route is redirected to the Shopify Admin page for the current storefront. Disable this redirect by passing `true`. \*/
noAdminRedirect?: boolean;
/** By default, query parameters are not used to match redirects. Set this to `true` if you'd like redirects to be query parameter sensitive \*/
matchQueryParams?: boolean;
};
/\*\*

- Queries the Storefront API to see if there is any redirect
- created for the current route and performs it. Otherwise,
- it returns the response passed in the parameters. Useful for
- conditionally redirecting after a 404 response.
-
- @see {@link https://help.shopify.com/en/manual/online-store/menus-and-links/url-redirect Creating URL redirects in Shopify}
  \*/
  declare function storefrontRedirect(options: StorefrontRedirect): Promise<Response>;

interface SeoConfig {
/**
_ The `title` HTML element defines the document's title that is shown in a browser's title bar or a page's tab. It
_ only contains text; tags within the element are ignored. \*
_ @see https://developer.mozilla.org/en-US/docs/Web/HTML/Element/title
_/
title?: Maybe<string>;
/**
_ Generate the title from a template that includes a `%s` placeholder for the title.
_
_ @example
_ `js
     * {
     *   title: 'My Page',
     *   titleTemplate: 'My Site - %s',
     * }
     * `
_/
titleTemplate?: Maybe<string> | null;
/\*\*
_ The media associated with the given page (images, videos, etc). If you pass a string, it will be used as the
_ `og:image` meta tag. If you pass an object or an array of objects, that will be used to generate `og:<type of
_ media>`meta tags. The`url`property should be the URL of the media. The`height`and`width`properties are
     * optional and should be the height and width of the media. The`altText`property is optional and should be a
     * description of the media.
     *
     * @example
     * ```js
     * {
     *   media: [
     *     {
     *       url: 'https://example.com/image.jpg',
     *       type: 'image',
     *       height: '400',
     *       width: '400',
     *       altText: 'A custom snowboard with an alpine color pallet.',
     *     }
     *   ]
     * }
     * ```
     *
     */
    media?: Maybe<string> | Partial<SeoMedia> | (Partial<SeoMedia> | Maybe<string>)[];
    /**
     * The description of the page. This is used in the`name="description"`meta tag as well as the`og:description`meta
     * tag.
     *
     * @see https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta
     */
    description?: Maybe<string>;
    /**
     * The canonical URL of the page. This is used to tell search engines which URL is the canonical version of a page.
     * This is useful when you have multiple URLs that point to the same page. The value here will be used in the
     *`rel="canonical"`link tag as well as the`og:url`meta tag.
     *
     * @see https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link
     */
    url?: Maybe<string>;
    /**
     * The handle is used to generate the`twitter:site`and`twitter:creator`meta tags. Include the`@`symbol in the
     * handle.
     *
     * @example
     * ```js
     * {
     *   handle: '@shopify'
     * }
     * ```
     */
    handle?: Maybe<string>;
    /**
     * The`jsonLd`property is used to generate the`application/ld+json`script tag. This is used to provide structured
     * data to search engines. The value should be an object that conforms to the schema.org spec. The`type`property
     * should be the type of schema you are using. The`type`property is required and should be one of the following:
     *
     * -`Product`     * -`ItemList`     * -`Organization`     * -`WebSite`     * -`WebPage`     * -`BlogPosting`     * -`Thing`     *
     * The value is validated via [schema-dts](https://www.npmjs.com/package/schema-dts)
     *
     * @example
     * ```js
     * {
     *   jsonLd: {
     *     '@context': 'https://schema.org',
     *     '@type': 'Product',
     *     name: 'My Product',
     *     image: 'https://hydrogen.shop/image.jpg',
     *     description: 'A product that is great',
     *     sku: '12345',
     *     mpn: '12345',
     *     brand: {
     *       '@type': 'Thing',
     *       name: 'My Brand',
     *     },
     *     aggregateRating: {
     *       '@type': 'AggregateRating',
     *       ratingValue: '4.5',
     *       reviewCount: '100',
     *     },
     *     offers: {
     *       '@type': 'Offer',
     *       priceCurrency: 'USD',
     *       price: '100',
     *       priceValidUntil: '2020-11-05',
     *       itemCondition: 'https://schema.org/NewCondition',
     *       availability: 'https://schema.org/InStock',
     *       seller: {
     *         '@type': 'Organization',
     *         name: 'My Brand',
     *       },
     *     },
     *   }
     * }
     * ```
     *
     * @see https://schema.org/docs/schemas.html
     * @see https://developers.google.com/search/docs/guides/intro-structured-data
     * @see https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script
     *
     */
    jsonLd?: WithContext<Thing> | WithContext<Thing>[];
    /**
     * The`alternates`property is used to specify the language and geographical targeting when you have multiple
     * versions of the same page in different languages. The`url`property tells search engines about these variations
     * and helps them to serve the correct version to their users.
     *
     * @example
     * ```js
     * {
     *   alternates: [
     *     {
     *       language: 'en-US',
     *       url: 'https://hydrogen.shop/en-us',
     *       default: true,
     *     },
     *     {
     *       language: 'fr-CA',
     *       url: 'https://hydrogen.shop/fr-ca',
     *     },
     *   ]
     * }
     * ```
     *
     * @see https://support.google.com/webmasters/answer/189077?hl=en
     */
    alternates?: LanguageAlternate | LanguageAlternate[];
    /**
     * The`robots` property is used to specify the robots meta tag. This is used to tell search engines which pages
_ should be indexed and which should not.
_
_ @see https://developers.google.com/search/reference/robots_meta_tag
_/
robots?: RobotsOptions;
}
/\*\*

- @see https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag
  _/
  interface RobotsOptions {
  /\*\*
  _ Set the maximum size of an image preview for this page in a search results Can be one of the following: \*
  _ - `none` - No image preview is to be shown.
  _ - `standard` - A default image preview may be shown.
  _ - `large` - A larger image preview, up to the width of the viewport, may be shown.
  _
  _ If no value is specified a default image preview size is used.
  _/
  maxImagePreview?: 'none' | 'standard' | 'large';
  /**
  _ A number representing the maximum of amount characters to use as a textual snippet for a search result. This value
  _ can also be set to one of the following special values: \*
  _ - 0 - No snippet is to be shown. Equivalent to nosnippet.
  _ - 1 - The Search engine will choose the snippet length that it believes is most effective to help users discover
  _ your content and direct users to your site
  _ - -1 - No limit on the number of characters that can be shown in the snippet.
  \*/
  maxSnippet?: number;
  /**
  _ The maximum number of seconds for videos on this page to show in search results. This value can also be set to one
  _ of the following special values: \*
  _ - 0 - A static image may be used with the `maxImagePreview` setting.
  _ - 1 - There is no limit to the size of the video preview. \*
  _ This applies to all forms of search results (at Google: web search, Google Images, Google Videos, Discover,
  _ Assistant).
  _/
  maxVideoPreview?: number;
  /\*\*
  _ Do not show a cached link in search results.
  _/
  noArchive?: boolean;
  /\*\*
  _ Do not follow the links on this page. \*
  _ @see https://developers.google.com/search/docs/advanced/guidelines/qualify-outbound-links
  _/
  noFollow?: boolean;
  /**
  _ Do not index images on this page.
  _/
  noImageIndex?: boolean;
  /**
  _ Do not show this page, media, or resource in search results.
  _/
  noIndex?: boolean;
  /**
  _ Do not show a text snippet or video preview in the search results for this page.
  _/
  noSnippet?: boolean;
  /**
  _ Do not offer translation of this page in search results.
  _/
  noTranslate?: boolean;
  /**
  _ Do not show this page in search results after the specified date/time.
  _/
  unavailableAfter?: string;
  }
  interface LanguageAlternate {
  /**
  _ Language code for the alternate page. This is used to generate the hreflang meta tag property.
  _/
  language: string;
  /**
  _ Whether the alternate page is the default page. This will add the `x-default` attribution to the language code.
  _/
  default?: boolean;
  /**
  _ The url of the alternate page. This is used to generate the hreflang meta tag property.
  _/
  url: string;
  }
  type SeoMedia = {
  /**
  _ Used to generate og:<type of media> meta tag
  _/
  type: 'image' | 'video' | 'audio';
  /**
  _ The url value populates both url and secure_url and is used to infer the og:<type of media>:type meta tag.
  _/
  url: Maybe<string> | undefined;
  /**
  _ The height in pixels of the media. This is used to generate the og:<type of media>:height meta tag.
  _/
  height: Maybe<number> | undefined;
  /**
  _ The width in pixels of the media. This is used to generate the og:<type of media>:width meta tag.
  _/
  width: Maybe<number> | undefined;
  /\*\*
  _ The alt text for the media. This is used to generate the og:<type of media>:alt meta tag.
  _/
  altText: Maybe<string> | undefined;
  };

type GetSeoMetaReturn = ReturnType<MetaFunction>;
type Optional<T> = T | null | undefined;
/\*\*

- Generate a Remix meta array from one or more SEO configuration objects. This is useful to pass SEO configuration for the parent route(s) and the current route. Similar to `Object.assign()`, each property is overwritten based on the object order. The exception is `jsonLd`, which is preserved so that each route has it's own independent jsonLd meta data.
  \*/
  declare function getSeoMeta(...seoInputs: Optional<SeoConfig>[]): GetSeoMetaReturn;

interface SeoHandleFunction<Loader extends LoaderFunction | unknown = unknown> {
(args: {
data: Loader extends LoaderFunction ? Awaited<ReturnType<Loader>> : unknown;
id: string;
params: Params;
pathname: Location['pathname'];
search: Location['search'];
hash: Location['hash'];
key: string;
}): Partial<SeoConfig>;
}
interface SeoProps {
/** Enable debug mode that prints SEO properties for route in the console \*/
debug?: boolean;
}
/**

- @deprecated - use `getSeoMeta` instead
  \*/
  declare function Seo({ debug }: SeoProps): react.FunctionComponentElement<{
  children?: react.ReactNode | undefined;
  }>;

declare function ShopPayButton(props: ComponentProps<typeof ShopPayButton$1>): react_jsx_runtime.JSX.Element;

type SITEMAP*INDEX_TYPE = 'pages' | 'products' | 'collections' | 'blogs' | 'articles' | 'metaObjects';
interface SitemapIndexOptions {
/** The Storefront API Client from Hydrogen \*/
storefront: Storefront;
/** A Remix Request object */
request: Request;
/\*\* The types of pages to include in the sitemap index. \_/
types?: SITEMAP_INDEX_TYPE[];
/** Add a URL to a custom child sitemap \*/
customChildSitemaps?: string[];
}
/**

- Generate a sitemap index that links to separate sitemaps for each resource type. Returns a standard Response object.
  _/
  declare function getSitemapIndex(options: SitemapIndexOptions): Promise<Response>;
  interface GetSiteMapOptions {
  /\*\* The params object from Remix _/
  params: LoaderFunctionArgs['params'];
  /** The Storefront API Client from Hydrogen \*/
  storefront: Storefront;
  /** A Remix Request object _/
  request: Request;
  /\*\* A function that produces a canonical url for a resource. It is called multiple times for each locale supported by the app. _/
  getLink: (options: {
  type: string | SITEMAP*INDEX_TYPE;
  baseUrl: string;
  handle?: string;
  locale?: string;
  }) => string;
  /** An array of locales to generate alternate tags \*/
  locales?: string[];
  /** Optionally customize the changefreq property for each URL */
  getChangeFreq?: (options: {
  type: string | SITEMAP*INDEX_TYPE;
  handle: string;
  }) => string;
  /\*\* If the sitemap has no links, fallback to rendering a link to the homepage. This prevents errors in Google's search console. Defaults to `/`. */
  noItemsFallback?: string;
  }
  /\*\*
- Generate a sitemap for a specific resource type.
  \*/
  declare function getSitemap(options: GetSiteMapOptions): Promise<Response>;

export { Analytics, AnalyticsEvent, CacheCustom, type CacheKey, CacheLong, CacheNone, CacheShort, type CachingStrategy, type CartActionInput, CartForm, type CartLineUpdatePayload, type CartQueryDataReturn, type CartQueryOptions, type CartQueryReturn, type CartReturn, type CartUpdatePayload, type CartViewPayload, type CollectionViewPayload, type ConsentStatus, type CookieOptions, type CreateStorefrontClientForDocs, type CreateStorefrontClientOptions, type CustomEventMap$1 as CustomEventMap, type CustomerAccount, type CustomerAccountMutations, type CustomerAccountQueries, type CustomerPrivacy$1 as CustomerPrivacy, type CustomerPrivacyApiProps, type CustomerPrivacyConsentConfig, type HydrogenCart, type HydrogenCartCustom, type HydrogenContext, type HydrogenEnv, type HydrogenRouterContextProvider, type HydrogenSession, type HydrogenSessionData, type I18nBase, InMemoryCache, type MetafieldWithoutOwnerId, type NoStoreStrategy, NonceProvider, type OptimisticCart, type OptimisticCartLine, type OptimisticCartLineInput, OptimisticInput, type PageViewPayload, Pagination, type PrivacyBanner$1 as PrivacyBanner, type ProductViewPayload, RichText, Script, type SearchViewPayload, Seo, type SeoConfig, type SeoHandleFunction, type SetConsentHeadlessParams, type ShopAnalytics, ShopPayButton, type Storefront, type StorefrontApiErrors, type StorefrontClient, type StorefrontForDoc, type StorefrontMutationOptionsForDocs, type StorefrontMutations, type StorefrontQueries, type StorefrontQueryOptionsForDocs, type VariantOption, type VariantOptionValue, VariantSelector, type VisitorConsent, type VisitorConsentCollected, type WithCache, cartAttributesUpdateDefault, cartBuyerIdentityUpdateDefault, cartCreateDefault, cartDiscountCodesUpdateDefault, cartGetDefault, cartGetIdDefault, cartGiftCardCodesAddDefault, cartGiftCardCodesRemoveDefault, cartGiftCardCodesUpdateDefault, cartLinesAddDefault, cartLinesRemoveDefault, cartLinesUpdateDefault, cartMetafieldDeleteDefault, cartMetafieldsSetDefault, cartNoteUpdateDefault, cartSelectedDeliveryOptionsUpdateDefault, cartSetIdDefault, changelogHandler, createCartHandler, createContentSecurityPolicy, createCustomerAccountClient, createHydrogenContext, createRequestHandler, createStorefrontClient, createWithCache, formatAPIResult, generateCacheControlHeader, getPaginationVariables, getSelectedProductOptions, getSeoMeta, getShopAnalytics, getSitemap, getSitemapIndex, graphiqlLoader, hydrogenContext, hydrogenPreset, hydrogenRoutes, storefrontRedirect, useAnalytics, useCustomerPrivacy, useNonce, useOptimisticCart, useOptimisticData, useOptimisticVariant };

```

```
---

## ⚠️ MANDATORY: Search Before Writing Code

Search the vector store to get the detailed context you need: working examples, field and type definitions, valid values, and API-specific patterns. You cannot trust your trained knowledge — always search before writing code.

```
scripts/search_docs.mjs "<component tag name>" --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION
```

Search for the **component tag name**, not the full user prompt.

For example, if the user asks about cart UI:
```
scripts/search_docs.mjs "CartForm component" --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION
```

## ⚠️ MANDATORY: Validate Before Returning Code

You MUST run `scripts/validate.mjs` before returning any generated code to the user. Always include the instrumentation flags:

```
scripts/validate.mjs --code '...' --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER
```
(For YOUR_ARTIFACT_ID, generate a stable random ID per code block and reuse it across validation retries. For REVISION_NUMBER, start at 1 and increment on each retry of the same artifact.)

**When validation fails, follow this loop:**
1. Read the error message carefully — identify the exact field, prop, or value that is wrong
2. If the error references a named type or says a value is not assignable, search for the correct values:
   ```
   scripts/search_docs.mjs "<type or prop name>"
   ```
3. Fix exactly the reported error using what the search returns
4. Run `scripts/validate.mjs` again
5. Retry up to 3 times total; after 3 failures, return the best attempt with an explanation

**Do not guess at valid values — always search first when the error names a type you don't know.**

---

> **Privacy notice:** `scripts/search_docs.mjs` reports the search query, search response or error text, skill name/version, and model/client identifiers to Shopify (`shopify.dev/mcp/usage`) to help improve these tools. Set `OPT_OUT_INSTRUMENTATION=true` in your environment to opt out.

---

> **Privacy notice:** `scripts/validate.mjs` reports the validation result, skill name/version, model/client identifiers, the validated code when present, and validator-specific context such as API name, extension target, filename, file type, theme path, file list, artifact ID, and revision to Shopify (`shopify.dev/mcp/usage`) to help improve these tools. Set `OPT_OUT_INSTRUMENTATION=true` in your environment to opt out.
