#include<math.h>
#include<iostream>

/* STEPS

Need info:
  Distance from computer
  Four corners of computer screen
  Eye position
  Eye rotation

1) Use eye position/rotation to make a 3d gaze direction

2) Map that to the computer box

*/

// [name] = [negative]/[positive]
// x = left/right
// y = in/out
// z = down/up
// pitch = down/up
// yaw = left/right

//struct that represents a blob detected from the sensor
struct IRPoint {
  int x, y, area, radius;
};

struct Point {
  double x, y;
};

struct Point3D {
  double x, y, z; // represent location relative to headset in cm
};

struct Vector3D {
  double x, y, z;
};

struct Ray3D {
  Point3D pos;
  Vector3D direction; 
};

IRPoint topLeft;
IRPoint topLeftMarker; // a little to the left of topleft
IRPoint leftTopMarker; // a little under topLeft
IRPoint topRight;
IRPoint bottomLeft;
IRPoint bottomRight;

const Point3D EYE_POSITION = {-3.0, 0.0, -1.0};

// Eye angles
double eyePitch = 0.0; // higher --> up
double eyeYaw = 0.0; // higher --> left

void setup() {
  // Serial.begin(9600);
}

//Returns an array of IRPoint, containing the eye blobs 
struct IRPoint *getEyePoints(){}

//Returns an array of IRPoint, containing the front-facing blobs
struct IRPoint *getScreenCorners(){}

bool isLeftBlinking() { return false; }
bool isRightBlinking() { return false; }

// returns the Points on the screen in 3d space
struct Point3D* getScreenCorners3D(IRPoint* screenCorners2D) {}

struct Ray3D getLeftEyeState() {} // Get rotations of eyes
struct Ray3D getRightEyeState() {} // Get rotations of eyes

/* Finds cross product of two vectors by
calculating this determinant:
[ x     y     z   ] [i/j/k]
[ a.x   a.y   a.z ]
[ b.x   b.y   b.z ]
*/
struct Vector3D cross(Vector3D a, Vector3D b) {
  return {
    a.y * b.z - a.z * b.y,
    -(a.x * b.z - a.z * b.x),
    a.x * b.y - a.y * b.x
  };
}

// Solves a set of linear equations using Gaussian elimination
// From StackOverflow
void solve(double matrix[], int rows, int cols) {
  for (int i = 0; i < cols - 1; i++) {
    for (int j = i; j < rows; j++) {
      if (matrix[i + j * cols] != 0) {
        if (i != j)
          for (int k = i; k < cols; k++) {
            double temp = matrix[k + j * cols];
            matrix[k + j * cols] = matrix[k + i * cols];
            matrix[k + i * cols] = temp;
          }

        j = i;

        for (int v = 0; v < rows; v++) {
          if (v != j) {
            double factor = matrix[i + v * cols] / matrix[i + j * cols];
            matrix[i + v * cols] = 0;

            for (int u = i + 1; u < cols; u++)
            {
              matrix[u + v * cols] -= factor * matrix[u + j * cols];
              matrix[u + j * cols] /= matrix[i + j * cols];
            }
            matrix[i + j * cols] = 1;
          }
        }
        break;
      }
    }
  }
}

// https://stackoverflow.com/questions/29188686/finding-the-intersect-location-of-two-rays
struct Ray3D getRayIntersection(Ray3D ray1, Ray3D ray2) {
  Vector3D direction3 = cross(ray1.direction, ray2.direction);

  // [d1.X  -d2.X  d3.X | p2.X - p1.X]
  // [d1.Y  -d2.Y  d3.Y | p2.Y - p1.Y]
  // [d1.Z  -d2.Z  d3.Z | p2.Z - p1.Z]

  double matrix[12];
  matrix[0] = ray1.direction.x;
  matrix[1] = -ray2.direction.x;
  matrix[2] = direction3.x;
  matrix[3] = ray2.pos.x - ray1.pos.x;

  matrix[4] = ray1.direction.y;
  matrix[5] = -ray2.direction.y;
  matrix[6] = direction3.y;
  matrix[7] = ray2.pos.y - ray1.pos.y;

  matrix[8] = ray1.direction.z;
  matrix[9] = -ray2.direction.z;
  matrix[10] = direction3.z;
  matrix[11] = ray2.pos.z - ray1.pos.z;
  
  // solve with Gaussian elimination
  solve(matrix, 3, 4);
  
  double a = matrix[3];
  double b = matrix[7];
  double c = matrix[11];

  if (a >= 0 && b >= 0) {
    return {
      {
        ray1.pos.x + ray1.direction.x * a,
        ray1.pos.y + ray1.direction.y * a,
        ray1.pos.z + ray1.direction.z * a,
      }, // Point3D
      {
        direction3.x * c,
        direction3.y * c,
        direction3.z * c
      } // Vector3D
    };
  } else {
    return {{0, 0, 0}, {0, 0, 0}};
  }
}

struct Point getGazeScreenPoint(Point3D* screenCorners, Point3D gazePoint) {
  // returns location on screen that you're looking at
  // yaw = left/right, pitch = up/down

  // This code extends a vector from the eyePosition until it intersects the plane created by screenCorners
  // Then, it finds the relative location within screenCorners of the gaze vector

  // If it's out of bounds, returns the numbers anyway
}

//Checks if a Point eye fits in a given paralellogram
bool fitsInParallelogram(IRPoint *parallelogram, IRPoint eye) {}

//Given that eye is within the parallelogram, scale/normalize the parallelogram and return a Point 
//with coords between 0 and 1 with respect to screen bounds. (Note: Point is not the same as IRPoint)
struct Point scaleUniformReturn (IRPoint *parallelogram, IRPoint eye) {}

//Send to Computer thru bluetooth or wifi direct idrk
//Actions : 'M' = "Move", 'C' = "Click" add more if u want
void sendToComputer(double x, double y, char action) {}

void loop() {
  Ray3D leftEye = getLeftEyeState();
  Ray3D rightEye = getRightEyeState();

  Ray3D gazePoint = getRayIntersection(leftEye, rightEye);
  Point3D *screenCorners = getScreenCorners3D(getScreenCorners());

  Point gazeScreenPoint = getGazeScreenPoint(screenCorners, {0, 0, 0});

  char action = 'M';
  if (isLeftBlinking() && !isRightBlinking()) {
    action = 'C';
  }

  sendToComputer(gazeScreenPoint.x, gazeScreenPoint.y, action);

}

int main() {
  Ray3D leftEye;
  Ray3D rightEye;

  leftEye.pos = {-1, 0, 0}; // left of camera
  rightEye.pos = {1, 0, 0}; // right of camera

  leftEye.direction = {1, 1, 0}; // forward/right of camera
  rightEye.direction = {-1, 1, 0}; // forward/left of camera

  Ray3D inter = getRayIntersection(leftEye, rightEye);

  std::cout << "{" <<
    inter.pos.x << ", " <<
    inter.pos.y << ", " <<
    inter.pos.z << "} \n";

  std::cout << "{" <<
    inter.direction.x << ", " <<
    inter.direction.y << ", " <<
    inter.direction.z << "} \n";
}