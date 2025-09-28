`tmx4ml` uses a query syntax mostly compatible with the one used in TMX, while providing useful extensions for better ease of use in a text-only environment.

# Common syntax elements

- **Parameter**: Search parameters are provided using the `param:value` format, where `param` is the name of the option, to which is provided a `value`
- **Parameter list**: Some parameters might accept a list of multiple values, these can be separated using commas.
- **Date**: Dates are provided in the `YYYY-MM-DD` format. Example: `2025-08-25`
- **Time**: Times can be provided using the format `1h1m1s` to indicate hours, minutes and seconds; all of them are optional an can be skipped. Examples: `1m30s`, `20s`.
- **Range**: Ranges are indicated in the `lower-bound...upper-bound` format, with bounds separated by `...`, either of them being optional and can be empty. Examples: `2024-01-01...2024-12-31`, `30s...`.

## Track queries

Any non-parameter text will be used to search tracks by name.

Parameters:

### `antispam`

Values: `newest`, `awarded`

Filters multiple tracks by the same mapper. Use `newest` to only get the newest tracks, or `awarded` for the last awarded.

### `length`

Values: Range of Time

Filter tracks by length. Can provide either a minimum or maximum length, or both.

### `authoruserid`

Values: Number

Filter tracks by the TMX ID of one of their authors.

### `author`, `awardedby`, `commentedby`

Values: String

Filter tracks by the TMX name of one of their author, award giver or commenter, respectively.

### `difficulty`

Values: List of `beginner`, `intermediate`, `expert`, `lunatic`

Filter tracks by the difficulty. Multiple difficulties can be provided by separating them with commas.

### `environment`, `vehicle`, `car`

Values: List of `snow`, `desert`, `rally`, `island`, `coast`, `bay`, `stadium`

Filter by environment/vehicle. Multiple values can be provided separated by commas.

### `id`

Values: List of Number

Find tracks by their TMX ID; use commas to provide more than one ID.

### `in`

Values: List of `hasrecord`, `unlimiter`, `supporter`, `envmix`, `latestauthor`, `latestawardedauthor`, `screenshot`, `collaborative`, `featured`, `beta`

Set collections to filter for. Prefix any collection name with a `!` to invert the results. Valid collection names are:

* `hasrecord`: Track has replays submitted
* `unlimiter`: Track requires using Unlimiter to play it
* `supporter`: Author is a TMX supporter
* `envmix`: Track is envimix; car is different from environment
* `latestauthor`: Is the uploader's latest track
* `latestawardedauthor`: Is the uploader's latest awarded track.
* `screenshot`: Has custom screenshot
* `collaborative`: Track has multiple authors
* `featured`: Has been featured in the TMX front page
* `beta`: Search in beta area tracks

### `lbtype`

Values: `standard`, `classic`, `nadeo`, `uncompetitive`, `beta`, `star`

Filter by leaderboard

### mood

Values: List of `sunrise`, `day`, `sunset`, `night`

Filter tracks by mood. Multiple moods can be provided by separating them with commas.

### `order1`, `order2`

Values: Ascending or descending of `uploaded`, `updated`, `awards`, `comments`, `activity`, `trackname`, `authorname`, `difficulty`, `downloads`, `replayscore`, `awardsweek`, `awardsmonth`, `awarded`, `worldrecordset`, `userrecordset`, `userawarded`, `userdownloaded`, `usercommented`, `userrecordposition`, `tracklength`, `worldrecordtime`, `userrecordtime`, `trackpackposition`

Set result ordering; tracks are sorted first by the `order1` parameter, and second by `order2`. Any of the accepted values must be appended with either `asc` or `desc` to indicate the ordering, either ascending (lowest to highest) or descending (highest to lowest)

### `packid`

Values: Number

Show only tracks from track pack with the given id.

### `routes`

Values: `single`, `multiple`, `symmetric`

Filter tracks by routes.

### `tags`

Values: List of `normal`, `stunt`, `maze`, `offroad`, `multilap`, `fullspeed`, `lol`, `tech`, `speedtech`, `rpg`, `pressforward`, `trial`, `grass`, `story`, `nascar`, `speedfun`, `endurance`, `alterednadeo`, `transitional`

Filter tracks by its tags. Prefix a tag name with `!` to exclude tracks with that tag. By default, this requires the track to contain all requested tags; use the `taginclusive` parameter to change this behavior.

### `taginclusive`

Values: `true`, `false`

Setting this to `true` (the default), will require results to contain all tags requested in the `tags` parameter. A value of `false` includes tracks that contain any of the `tags`

### `type`

Values: `race`, `puzzle`, `platform`, `stunts`

Filter by track game mode.

### `uploaded`

Values: Range of Date

Filter tracks by upload date. Can provide either a minimum or maximum date, or both.

### `value`

Values: Range of Number

Filter tracks by leaderboard value. Can provide either a minimum or maximum value, or both.

## Trackpack queries

Any non-parameter text will be used to search trackpacks by name.

Parameters:

### `creator`

Values: String

Filter trackpacks by creator name.

### `id`

Values: List of Number

Find trackpack by their TMX ID. Use commas to indicate multiple IDs.

### `order1`, `order2`

Values: Ascending or Descending of `uploaded`, `updated`, `tracks`, `activity`, `packname`, `authorname`, `download`, `trackpackvalue`

Set result ordering; packs are sorted first by the `order1` parameter, and second by `order2`. Any of the accepted values must be appended with either `asc` or `desc` to indicate the ordering, either ascending (lowest to highest) or descending (highest to lowest)

### `trackid`

Values: Number

Find trackpacks containing the track with the provided ID.

## User queries

Any non-parameter text will be used to search users by name.

Parameters:

### `id`

Values: List of Number

Find users with the provided IDs. Use commas to separate multiple IDs.

### `in`

Set collections to filter for. Prefix any collection name with a `!` to invert the results. Valid collection names are:

* `supporter`: User is a TMX supporter
* `moderator`: User is a TMX moderator

### `order1`, `order2`

Values: Ascending or Descending of `name`, `tracks`, `trackpacks`, `trackawards`, `trackawardsout`, `trackcomments`, `trackcommentsout`, `forumposts`, `forumthreads`, `registered`, `videosposted`, `videoscreated`, `replaycount`, `favorites`, `achievements`, `authormedals`, `goldmedals`, `silvermedals`, `bronzemedals`

Set result ordering; packs are sorted first by the `order1` parameter, and second by `order2`. Any of the accepted values must be appended with either `asc` or `desc` to indicate the ordering, either ascending (lowest to highest) or descending (highest to lowest)

### `tracks`, `awards`, `awardsgiven`

Values: Range of Number

Filter users by how many tracks they have uploaded, how many awards they have received or how many awards they've given, respectively

### `registered`

Values: Range of Date

Filter by the user's registration date.

## Leaderboard queries

Any non-parameter text will be used to search users by name.

Parameters:

### `lbenv`

Values: `all`, `snow`, `desert`, `rally`, `island`, `coast`, `bay`, `stadium`

Search in environment-specific leaderboard

### `lbid`

Values: Number or one of `standard`, `classic`, `nadeo`, `uncompetitive`, `beta`, `star`

Search in a specific leaderboard type. If a number is provided, search in the leaderboard for the trackpack with the given ID

### `order1`

Values: Ascending or Descending of `score`, `replays`, `worldrecords`, `top10s`

Set result ordering. Any of the accepted values must be appended with either `asc` or `desc` to indicate the ordering, either ascending (lowest to highest) or descending (highest to lowest)
