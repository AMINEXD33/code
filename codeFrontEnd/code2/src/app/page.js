import Image from "next/image";
import styles from "./page.module.css";
import Logo from "../(components)/logo/logo";
import "./landingpage.css";
import feature1 from "../../public/landingpagedeatures/create_anew_session_.png";
import feature2 from "../../public/landingpagedeatures/live_data.png";
import feature3 from "../../public/landingpagedeatures/users_allowed_inthe_session.png";
import feature4 from "../../public/landingpagedeatures/after_selecting_session.png";


export default function Home() {
  return (
    <div className="master">
      <div className="anchors">
        <Logo />
        <div className="links_">
          <a href="#intro">Intro</a>
          <a href="#feature">Feature</a>
          <a href="#about">About</a>
        </div>
      </div>
      <section className="flex_section" id="intro">
        <Logo id="thisoneid" />
        <div className="blabla">
          <div className="question">What is code</div>
          <div className="answer">
            <p>
              code is a coding platform that helps students take tests
              in a more easie and inovative way , by coding in a platform
              this makes it a plesent expirience for the students and an
              easy task for the teachers to manage the correction of the code
            </p>
          </div>
        </div>
        <div className="blabla this2">
          <a className="gotoplat" href="/login">GO TO THE PLATFORM</a>
        </div>
      </section>


      <section className="flex_section" id="feature">
        <div className="blabla">
          <div className="question">Features</div>
          <div className="features_container">

            <div className="feature">
              <div className="photo">
                <Image
                  src={feature1}
                  height={891}
                  width={1280}
                  alt="feature photo"
                  id="featureid1"
                  className="featurepht"
                />
              </div>
              <div className="feature_desc">
                <div className="feature_title">
                  add new session as admin
                </div>
                <div className="feature_dec">
                  as admin you can add new session , dictated what
                  programming languages to be used, and if the students
                  are allowed to run the code or not.
                </div>
              </div>
            </div>



            <div className="feature" id="feature2">
              <div className="photo">
                <Image
                  src={feature2}
                  height={891}
                  width={1280}
                  alt="feature photo"
                  id="featureid1"
                  className="featurepht"
                />
              </div>
              <div className="feature_desc">
                <div className="feature_title">
                  visiualize session data
                </div>
                <div className="feature_dec">
                  metrics about the session will be showed to the admin in the dashboard
                </div>
              </div>
            </div>


            <div className="feature" id="feature2">
              <div className="photo">
                <Image
                  src={feature3}
                  height={891}
                  width={1280}
                  alt="feature photo"
                  id="featureid1"
                  className="featurepht"
                />
              </div>
              <div className="feature_desc">
                <div className="feature_title">
                  manage users
                </div>
                <div className="feature_dec">
                  an admin can manage studenst see their stats or code ,
                  or even block a students from partisipating in the session
                </div>
              </div>
            </div>


            <div className="feature" id="feature2">
              <div className="feature_desc">
                <div className="feature_title">
                  students coding
                </div>
                <div className="feature_dec">
                  students can simply choose a session and start coding.

                </div>
              </div>

              <div className="photo">
                <Image
                  src={feature4}
                  height={891}
                  width={1280}
                  alt="feature photo"
                  id="featureid1"
                  className="featurepht"
                />
              </div>
            </div>
            <div className="about">
              <h1>about</h1>
              <div className="question">
                what inspired the project
              </div>
              <div className="answer">
                {`
                it's simply alot computer science people are dying inside from taking
                tests using a pen and papper, and I'm one of them, so this project is trying
                to change that
                `}
              </div>

            </div>



          </div>
        </div>

      </section>
    </div>
  );
}
