<p align="center">
  <img src="doc/logo.png" width="150">
</p>

<h1 align="center">Flerken</h1>

<p align="center">
  
  <img src="https://img.shields.io/badge/python-3.x-orange.svg" alt="python 3.x">
  <img src="http://img.shields.io/badge/license-APL2-brightgreen.svg?style=flat" alt="license">
  
</p>

## Introduction

<b>Command Line Obfuscation (CLOB) </b>has been proved to be a non-negligible factor in fileless malware or malicious actors that are "living off the land". With dozens of obfuscation tools seen in the wild, by contrast few proper countermeasures can be found. In this talk, we present Flerken, an obfuscation detection approach that works for both Windows (Powershell and CMD) and Linux (Bash) commands. To the best of our knowledge, Flerken is the first solution that supports cross-platform obfuscation detection feature.

This talk first shares some key observations on CLOB such as its attack vectors and analyzing strategies. Then we give a detailed design of Flerken. The description is divided in two parts, namely <b>Kindle (for Windows)</b> and <b>Octopus (for Linux)</b>. Respectively, we will show how human readability can serve as an effective statistical feature against PS/CMD obfuscation, and how dynamic syntax parsing can be adopted to eliminate false positives/negatives against Bash CLOB. The effectiveness of Flerken is evaluated via representative black/white command samples and performance experiments. 

Hereby, we highlight the functional properties Flerken basically satisfies as follows:

• <b>Scalability.</b> Flerken supports cross-platform obfuscation detection. Furthermore, Flerken can help achieve real-time obfuscation bubbling in server EDR systems (with a scale on the order of millions).

• <b>Accuracy.</b> Flerken is adequate to correctly distinguish most Windows/Linux command obfuscations. Therefore, Flerken can be adopted by enterprises in many security investigations of server endpoints.

• <b>Availability.</b> Flerken now is accessible through its official webpage. All you have to do is to paste into the command string and test what you want to analyze. No specific input file format is required. We have also open-sourced Flerken on Github so you can build your own detector on demand.

## Upcoming Release

- **De-Obfuscated-Bash Tool: An image of the octopusbash-embedded docker.**
- **A Web Console** to manage and config **bi-directional feature ring of Octopus**, **Gradient Boost Decision Tree Machine Learning of Kindle** and **docker containers cluster** etc.

## Getting Help

If you have any question or feedbacks on Flerken. Please create an issue and choose a suitable label for it. We will solve it as soon as possible.

<p align="center">
  <img src="doc/labels.png" width="95%">
</p>

## CHANGELOG

Please see our <a href="./CHANGELOG.md">CHANGELOG.md</a>


## Authors

- <a href="https://www.researchgate.net/profile/Yao_Zhang80" target="_blank">Yao Zhang</a>
- <a href="https://lightrains.org" target="_blank">Zhiyang Zeng</a>

## Acknowledgments

We would like to thank all the contributors to this research project and all the members in Tencent Blade Team. In addition, we would like to thank security researchers Daniel Bohannon and Andrew LeFevre for their valuable feedback and discussion.

## License

Flerken is released under the Apache 2.0 license.
