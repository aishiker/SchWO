# Phase 5 T4ac Literal Failed-Child Radial Gate

Decision: `GREEN / LITERAL FAILED-CHILD RADIAL GATE READY`.

## Contract and result

The gate evaluates exactly the 41 literal failed-child midpoint frequencies
frozen by the reviewed T4ac package. It covers both sectors, all eight Table-I
points, and every `ell=2..ell_max` under the unchanged lmax seed rule (maximum
360). It is radial-only and is not a uniform/full grid or recursive scan.

- Classification records: 146,416 unique complete Cartesian keys.
- Classification counts: 140,096 default-covered, 6,270 structured uncovered,
  50 structured solver-failed, zero default-other.
- Measured sector-aware transitions: 6,320.
- Direct-oracle validations: 6,320/6,320.
- Maximum oracle effective residual: `8.751294801378416e-16`.
- Maximum oracle relative sensitivity: `1.7849602030606062e-07`.
- Sensitivity anchors: 300/300 passed.
- Integrated-adapter preflight: 6,320/6,320 passed, zero failures.
- Preflight maximum relative `psi`, `dpsi_dr`, and `A_out`: all zero.

## Provenance

- Candidate/parent: `f3a64522642abfaa2e0f3933125df06ae76895e4` /
  `fa22f20f775c1b15ae533c03047d156687e5f3bf`.
- Implementation commit: `6e86d8b419d8c09af38e226400f7439f7cdfed79`.
- Classification snapshot:
  `e675b751fd4beae2446597034b99f847e0cc3528551bfc30f8efd3460ad944fe`.
- Final-adapter snapshot:
  `8188b306fea0190654f752190f0ab6e96ef6970b16fea704b9cdb99ca96c7ccc`.
- Root hashes: classification `e5c934568ff1a9f80838df3fc674fea153e4c638777e6d7c9c2c2d32d0024e5b`;
  oracle `b4954a152aa81853fe53931bcb9ee9820b6d6da6d923019288f276d0519c52c6`;
  preflight `08b5542a26c0b95f6bf10005aeb21681f75735f53b924f894f1c133081ee2873`;
  manifest `6b55500aae750f7b2400627825220f18e2ca9f608a4c977707e4f2ec363e78c8`.

## Exact five implementation blobs

- runner: git blob `693b764bb13f0fb0c74d0a8eddc2b930bbf48365`, SHA-256
  `59393981640f491ab8830898eefa455e1111cc57b07aab2f9b79ea72454543bb`.
- envelope: git blob `0ee1f3dbc829bd6e4debf0f0de4db90501919204`, SHA-256
  `0eee55a569c3e65632e417a107d906e4881b702393a3ed69dd4c6ef9484015e0`.
- radial solver: git blob `c1237739e0002024c802272564167cc590d37f7f`, SHA-256
  `d818aff2aeaa38946a4212102cef984e92c265e7c1432d1eee88acc535c896b4`.
- integration-design tests: git blob `14cbdd496ef55af300bf5ce5a4c79c71501236c1`,
  SHA-256 `9be7f0fc0158ae964e4df5355b364753bcc9f62df40cc5c0c33aef06469a28f4`.
- radial tests: git blob `5ab4ed9620de8aeef2bfce725cf8740a10c43924`, SHA-256
  `20816ea56b8ff71a98301b28fcc67b3408e77dba9686dcd446bb20ecb66df4de`.

## Ordered checkpoint SHA-256

```text
0.3125  045a471de3a69905bcf27abad87779abf87367c88484ddb4b89353d6b2847602
0.3375  eb477cbf2f215a1c7ad27c307de295784ae2c1d17ebaa585c22f8b1407f0a09b
0.3625  9a6bd9f071947c506d3fcb0991bf35c23b67a441cb7823d75d85be8b93bd4d98
0.3875  3a84f366bd85f59b675f73a6811c7df89b79a1ffd82809cc233fd227e66f7a9d
0.8625  b4e9acfb589f6b728ae2a71bfea1af4548282d326c8d290b8774139a99db968e
0.9125  eb6b4cffa464d2ff50e3065d795172868a2496c0f71de3cf6016a5e1149b420c
0.9375  f7289a0b133f181470b0cd5b3db5703d88a02d2b91310eaf871eb9cdabd170ad
0.9625  d715e25291c0fb141211d20ad9039e382666257ebad0fd38bcc21d501842750e
0.9875  9503699089a5f26ccf880cdde448121a5a53ed7def28fe4bf2484b0cc6f56238
1.5125  9c34208211d3ebb8b70c54d529df117e3105385afba7cfce420b6af1218c5640
1.5375  82966dd4b290de04a2070bfbf427441dc7c5183f5a8ef792de2ec91d4617ff4f
1.5625  cb63bcbdf1609d9cfcb662093b549884b8b0f537cb27fc12b498f658336063e9
1.5875  6284d277a3b7bb515104c0e3a3d062d6bfe56f46ba482690b3bc9565611340ff
1.6125  baa560533609cbb198207b1f716d7d72e3b4c59ba4d9e904ab39eec3d66efce0
1.6375  74f5cee5164c2f9bf01aa6160e22030de76433b904aec9ee22f0a0dbcc879f8e
1.6625  b923aaf86c739c75116a6eb756826ae0b419a1f4c95697a8998e1f8c50fcc69b
1.6875  03979f86950dac802c05bb32c30b33b05a6e0d753079e8603df079d4d5565b52
1.70625 2955e25de52309fae0bc2246373884f3e94744bf4d4bafdb62aa4026bf2cb14f
1.71875 337b18cffdec73519863a21c826e25f01415fbd21f6ef421430b5035e49bc0c4
2.78125 ae20969ea9a448266ce65d7d6213a5f3b65fabe049c9667625e8c12ba40c003a
2.79375 3f551731c651b396af617ee48b2ca15551e07572031ac2ff6f2aa591808a7641
2.8125  8e5933cd8805190f7fd8b84bc5978373a4dde275bb182c923a43dfcfd9903f3a
2.8375  aba0bbcd650de1fbf72f39bc914269543a0f7f01151caac5b750faff77fe022b
2.8625  11cfd178efaa07062e5f0b008adf2c7eb653c94ef1de6ce7ad4c2a0a1e0e6a67
2.8875  d564427b9975d18998e0cab85ea22f313e6c4896b23932eabd17a8c4f29191b5
2.9125  ab57a17a426d8cbb90104e1c3957d008e16a0beec09e8a629bb10dad87b888f3
2.9375  48f59e23cfe36271da0e475867b423a5285d559ba3a043725f5a7255c10d65f1
2.9625  981fe04eb59ada05d6972d673ccf80f59f166445d571c246a50e5507374c1f6d
2.9875  17ee5aea2f255a41d021e5891f3dd517e75159786da6370bf71b42b2cd2debab
3.75625 d1710d0d81889965d2a4103a468cfc8061676cf1e0fa16186dc1ed5c61721cdd
3.76875 263571f67e8abe9cc0f7376eac49c904aca81158585ee3e6778d1ac063914b97
3.78125 b28721149e9f71e0ea4e9a4080b4693d0eb05f4c1a98fdcc1a0a681155a72bfd
3.79375 d0974a3031c83e70dc425d188e7414ad63366171eadcd088be416f9059c26704
3.8125  5e8aa995e2a501da2352d8b518ff7dccc026ae0747886a7458bf055261c9692f
3.8375  e920917e23490b435ae5b00bfa43833a81b91caa14a49fdc14800e91aa4046d5
3.8625  9b0edc08255fb888e807be3036207d2ecca1d211338e2d3daacc385f2805d3b2
3.8875  1f5549566a49006add5329f9c4f384dbbc59abe757c24e671bfbf48af38ddc08
3.9125  e2b0bd454a03a72ebd1da7a04a28149b146afd8eea4353413de493d084c7c3c9
3.9375  3dfc5caa4c8f30c332af6c27aeaf6cf8682a737fa71905c8d6c3dc54d8a9efdb
3.9625  f21863777e6da785ca042db7ce303be34f1d035a951febe0bde4fbe4f89eee81
3.9875  5dc959b31ed25bb89e34acbdadfc7b3471f3fa73c09015013f61485cfa5c9bf7
```

## Verification and non-claims

- Classification/oracle audit: PASS, 146,416 records, 6,320 transitions,
  41 checkpoints.
- Focused pytest: 4 passed, 352 deselected, 7 subtests passed.
- Exact-five-path Ruff: passed.
- Fresh full pytest: 659 passed, 117 skipped, 1 xfailed, 103 warnings,
  97 subtests passed in 317.17 s.
- No lmax extension, automatic/recursive midpoint, uniform/full grid,
  amplification, production, plot, fixture, Kirchhoff, paper-style output,
  downstream dispatch, replacement task, or GitHub action.
