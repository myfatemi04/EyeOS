
bool calibrated = false;

//struct that represents a blob detected from the sensor
struct irPoint {
  int x, y, area, radius;
};

struct point {
  double x, y;
};

//Constants that limit FOV and help during calibration to sync eye and front-facing cam
struct irPoint frontUp;
struct irPoint frontDown;
struct irPoint frontLeft;
struct irPoint frontRight;

//Change based on Calibration
struct irPoint eyeUp;
struct irPoint eyeDown;
struct irPoint eyeLeft;
struct irPoint eyeRight;


//e.g. frontUp and eyeUp will be looking at the same area in space,
//however frontUp will be from front-facing cam POV and eyeUp will be from eye cam POV

void setup() {
  Serial.begin(9600);

}

//Returns an array of irPoint, containing the eye blobs 
struct irPoint * getEyePoints(){}

//Returns an array of irPoint, containing the front-facing blobs
struct irPoint * getScreenCorners(){}

void loop() {
  if (!calibrated)
    calibrate();

  struct point look = calcLookPoint();
  if (look.x != -1.0 && !isBlinking()) sendToComputer(look.x, look.y, 'M');
  if (look.x != -1.0 && isBlinking()) sendToComputer(look.x, look.y, 'C');
    
}

//We can put these serial prints on a clear OLED screen so ppl know that to do
void calibrate()
{
  //Add some visual cue as to where to look; purpose is to sync user and front-facing sensor FOV 
  Serial.println("Without Moving Your head: ");
  
  Serial.println("Look at Up Object");
  delay(200);
  eyeUp = getEyePoints();
  Serial.println("Look at Down Object");
  delay(200);
  eyeDown = getEyePoints();
  Serial.println("Look at Left Object");
  delay(200);
  eyeLeft = getEyePoints();
  Serial.println("Look at Right Object");
  delay(200);
  eyeRight = getEyePoints();
  
  calibrated = true;
  
}

struct point calcLookPoint()
{   
    struct irPoint eyepoints[] = getEyePoints();
    struct irPoint frontpoints[] = getScreenCorners();

    struct irPoint eye = eyepoints[0];

    //Since both sensors have same res

    vertDiff = frontUp.y - eyeUp.y;
    horDiff = frontUp.x - eyeUp.x;

    eye.y += vertDiff;
    eye.x += horDiff;

    if (!fitsInParallelogram(frontpoints, eye) ) return struct point p = {-1.0, -1.0};

    return scaleUniformReturn(frontpoints, eye);
}

//Checks if a point eye fits in a given paralellogram
bool fitsInParalellogram(struct irPoint *parallelogram, struct irPoint eye)
{}

//Given that eye is within the parallelogram, scale/normalize the parallelogram and return a point 
//with coords between 0 and 1 with respect to screen bounds. (Note: Point is not the same as irPoint)
struct point scaleUniformReturn (struct irPoint *parallelogram, struct irPoint eye)
{}

//Get eye points and check if blinking over span of 100-200 ms
bool isBlinking() {}

//Send to Computer thru bluetooth or wifi direct idrk
//Actions : 'M' = "Move", 'C' = "Click" add more if u want
void sendToComputer(double x, double y, char action )
{}
 
