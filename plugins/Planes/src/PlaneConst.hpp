#ifndef PLANES_CONST_HPP
#define PLANES_CONST_HPP

// FIXME won't work unless correctly imported etc

// namespace...

constexpr double kEarthFlattening = 1.0 / 298.257223563;
constexpr double kEarthRadiusMeters = 6378137.0;
constexpr double kSecondsPerDay = 24 * 60 * 60;
constexpr double kMaxDeadReckoningSeconds = 30.0;
constexpr double kTrackingProbeSeconds = 1.0;
constexpr double kMetersToFeet = 3.280839895;
constexpr double kNauticalMilesToMeters = 1852.0;
constexpr double kMetersPerSecondToKnots = 60.0 * 60.0 / kNauticalMilesToMeters;
constexpr double kMetersPerSecondToFeetPerMinute = 60.0 * kMetersToFeet;
constexpr float kPlaneSpriteSize = 16.0f;
constexpr float kSpriteTrackingOffsetDegrees = -180.0f;

// FIXME these consts are unneccessary - should be simplified.
constexpr double kFeetToMeters = 1.0 / kMetersToFeet;
constexpr double kKnotsToMetersPerSecond = 1.0 / kMetersPerSecondToKnots;
constexpr double kFeetPerMinuteToMetersPerSecond = 1.0 / kMetersPerSecondToFeetPerMinute;

constexpr int kLabelModeFlightNumber = 0;
constexpr int kLabelModeAircraftModel = 1;
constexpr int kDefaultFetchIntervalSec = 15;
constexpr int kMinFetchIntervalSec = 15;
constexpr int kMaxFetchIntervalSec = 60;
constexpr int kDefaultRadiusNm = 250;
constexpr int kMinRadiusNm = 25; // why should there be a mimimum distance? if the user decides for '0', that's his choice...
constexpr int kMaxRadiusNm = 500; // probably not realistic
constexpr int kMaxPublishedAircraft = 200;

#endif

